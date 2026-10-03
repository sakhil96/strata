from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from .. import agent, narrate
from ..backend import PERSONAS
from ..schemas import AskRequest, BeforeAfterRequest, CompareRequest, QueryRequest
from .deps import backend, caller, pinned_persona

router = APIRouter(tags=["answers"])
COMPARE_ROLES = ("PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE")


def semantic_failure(exc: Exception) -> JSONResponse:
    detail = exc.as_dict() if hasattr(exc, "as_dict") else {"error": "query_failed", "message": str(exc)}
    return JSONResponse(status_code=422, content=detail)


def governed_answer(request: Request, who, query: dict[str, Any], question: str | None) -> dict[str, Any]:
    return backend().query(who, query, question)


def dimension_titles() -> dict[str, str]:
    return {d: meta.get("title", d) for spec in backend().registry.tables.values()
            for d, meta in spec.get("dimensions", {}).items()}


def told(answer: dict[str, Any], question: str, started: float) -> dict[str, Any]:
    return answer | {"lead": narrate.lead(answer, question, dimension_titles()),
                     "total_ms": int((time.perf_counter() - started) * 1000)}


def distinct(queries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen, kept = set(), []
    for q in queries:
        key = repr(sorted((k, repr(v)) for k, v in q.items()))
        if key not in seen:
            seen.add(key)
            kept.append(q)
    return kept


@router.post("/query", summary="Answer a structured semantic query without the model")
def structured_query(body: QueryRequest, request: Request):
    started = time.perf_counter()
    who = caller(request, body.persona)
    try:
        answer = governed_answer(request, who, body.query.model_dump(exclude_none=True), None)
    except ValueError as exc:
        return semantic_failure(exc)
    return told(answer, "", started) | {"path": "builder"}


@router.post("/ask", summary="Resolve with the governed agent, then answer as the caller's persona")
def ask(body: AskRequest, request: Request):
    # The agent only reads the question: it runs as the service's own role and its results are not
    # shown. Every canonical query it settled on is run again here as the caller's persona, on that
    # persona's semantic view, and that execution is the answer, its hash and its audit row.
    started = time.perf_counter()
    who = caller(request, body.persona)
    fallback_reason = None
    if agent.enabled():
        try:
            reply = agent.run(body.question, who.role, who.user, body.thread_id, body.parent_message_id)
            queries = distinct([a["canonical_query"] for a in reply["answers"] if a.get("canonical_query")])
            if queries:
                try:
                    answers = [governed_answer(request, who, q, body.question) for q in queries]
                except ValueError as exc:
                    return semantic_failure(exc)
                answers = [told(a, body.question, started) for a in answers]
                return answers[0] | {"answers": answers, "path": "agent", "reading": narrate.reading(reply["narrative"]),
                                     "fallback": False}
            if reply["refusal"]:
                backend().record_refusal(who, body.question, reply["refusal"])
                return {"path": "agent", "refusal": reply["refusal"], "fallback": False}
            fallback_reason = "the agent answered without settling on a governed query, so we did not use its answer"
        except agent.AgentUnavailable as exc:
            fallback_reason = str(exc)
    else:
        fallback_reason = "the agent is switched off in this environment"

    resolution = backend().resolve(who, body.question)
    if resolution["refusal"]:
        backend().record_refusal(who, body.question, resolution["refusal"])
        return {"path": "resolver", "refusal": resolution["refusal"], "fallback": True, "fallback_reason": fallback_reason}
    try:
        answer = told(governed_answer(request, who, resolution["query"], body.question), body.question, started)
    except ValueError as exc:
        return semantic_failure(exc)
    return answer | {"answers": [answer], "path": "resolver", "fallback": True, "fallback_reason": fallback_reason,
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


@router.get("/personas", summary="Roles this product can answer as, and the signed-in user's if it is fixed")
def personas(request: Request):
    pinned = pinned_persona(request)
    return {"default": pinned or request.app.state.default_role, "pinned": pinned is not None,
            "personas": list(PERSONAS)}
