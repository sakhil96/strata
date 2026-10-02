from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from .. import agent
from ..backend import PERSONAS
from ..schemas import AskRequest, BeforeAfterRequest, CompareRequest, QueryRequest
from .deps import backend, caller

router = APIRouter(tags=["answers"])
COMPARE_ROLES = ("PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE")


def semantic_failure(exc: Exception) -> JSONResponse:
    detail = exc.as_dict() if hasattr(exc, "as_dict") else {"error": "query_failed", "message": str(exc)}
    return JSONResponse(status_code=422, content=detail)


def governed_answer(request: Request, who, query: dict[str, Any], question: str | None) -> dict[str, Any]:
    return backend().query(who, query, question)


@router.post("/query", summary="Answer a structured semantic query without the model")
def structured_query(body: QueryRequest, request: Request):
    who = caller(request, body.persona)
    try:
        return governed_answer(request, who, body.query.model_dump(exclude_none=True), None) | {"path": "builder"}
    except ValueError as exc:
        return semantic_failure(exc)


@router.post("/ask", summary="Answer a question through the governed agent, or the resolver when it is down")
def ask(body: AskRequest, request: Request):
    who = caller(request, body.persona)
    degraded_reason = None
    if agent.enabled():
        try:
            reply = agent.run(body.question, who.role, who.user, body.thread_id, body.parent_message_id)
            if reply["answer"]:
                return reply["answer"] | {"path": "agent", "narrative": reply["narrative"], "degraded": False}
            if reply["refusal"]:
                backend().record_refusal(who, body.question, reply["refusal"])
                return {"path": "agent", "refusal": reply["refusal"], "narrative": reply["narrative"], "degraded": False}
            degraded_reason = "the agent answered without calling GOVERNED_QUERY, so we did not use its answer"
        except agent.AgentUnavailable as exc:
            degraded_reason = str(exc)
    else:
        degraded_reason = "the agent is switched off in this environment"

    resolution = backend().resolve(who, body.question)
    if resolution["refusal"]:
        backend().record_refusal(who, body.question, resolution["refusal"])
        return {"path": "resolver", "refusal": resolution["refusal"], "degraded": True, "degraded_reason": degraded_reason}
    try:
        answer = governed_answer(request, who, resolution["query"], body.question)
    except ValueError as exc:
        return semantic_failure(exc)
    return answer | {"path": "resolver", "degraded": True, "degraded_reason": degraded_reason,
                     "notes": answer["notes"] + resolution["notes"]}


@router.post("/compare", summary="Run one question under three roles and compare hashes and numbers")
def compare(body: CompareRequest, request: Request):
    if not (body.question or body.phrasings or body.query):
        raise HTTPException(status_code=422, detail="send a question, per-role phrasings, or a semantic query")
    columns = []
    for role in COMPARE_ROLES:
        who = caller(request, role)
        phrasing = (body.phrasings or {}).get(role) or body.question
        try:
            if body.query:
                query = body.query.model_dump(exclude_none=True)
            else:
                resolution = backend().resolve(who, phrasing)
                if resolution["refusal"]:
                    columns.append({"role": role, "phrasing": phrasing, "refusal": resolution["refusal"]})
                    continue
                query = resolution["query"]
            answer = governed_answer(request, who, query, phrasing)
        except ValueError as exc:
            return semantic_failure(exc)
        columns.append({"role": role, "phrasing": phrasing, "hash": answer["semantic_query_hash"],
                        "metric_name": answer["metric_name"], "rows": answer["rows"],
                        "value": headline(answer), "unit": answer["metrics"][0]["unit"], "ledger": answer})
    hashes = {c.get("hash") for c in columns}
    return {"columns": columns, "converged": len(hashes) == 1 and None not in hashes,
            "hash": hashes.pop() if len(hashes) == 1 else None}


def headline(answer: dict[str, Any]) -> float | None:
    metric = answer["canonical_query"]["metrics"][0]
    if answer["canonical_query"]["dimensions"] or not answer["rows"]:
        return None
    return answer["rows"][0][metric]


@router.post("/before-after", summary="Three legacy on-time numbers on RAW against the governed answer")
def before_after(body: BeforeAfterRequest, request: Request):
    who = caller(request, request.headers.get("x-persona") or "EXECUTIVE_ROLE")
    try:
        legacy = backend().legacy_otd(body.window)
        governed = governed_answer(request, who, {"metrics": ["on_time_delivery"], "time": {"range": body.window}},
                                   "before-after governed on-time delivery")
    except ValueError as exc:
        return semantic_failure(exc)
    return {"window": governed["canonical_query"]["time"], "legacy": legacy,
            "governed": {"value": headline(governed), "basis": governed["metrics"][0]["formula_text"],
                         "ledger": governed}}


@router.get("/personas", summary="Roles this product can answer as")
def personas(request: Request):
    return {"default": request.app.state.default_role, "personas": list(PERSONAS)}
