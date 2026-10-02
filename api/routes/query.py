"""POST /query — structured query path that works without the model."""

from __future__ import annotations

import json

from fastapi import APIRouter, Request

from ..schemas import QueryRequest, AnswerContract
from ..snowflake_client import get_connection, execute_procedure

router = APIRouter()


@router.post("/query", response_model=AnswerContract)
async def structured_query(body: QueryRequest, request: Request):
    """Execute a governed query directly through GOVERNED_QUERY, bypassing the agent."""
    persona = request.headers.get("X-Persona", "EXECUTIVE_ROLE")

    try:
        conn = get_connection(persona)
        result = execute_procedure(
            conn,
            "GOVERNED_QUERY",
            body.view,
            json.dumps(body.metrics),
            json.dumps(body.dimensions),
            json.dumps(body.time),
            json.dumps(body.filters),
        )
        conn.close()

        if "error" in result:
            return AnswerContract(error=result["error"], rows=[])

        return AnswerContract(
            rows=result.get("rows", []),
            sql=result.get("sql"),
            canonical_query=result.get("canonical_query"),
            semantic_query_hash=result.get("semantic_query_hash"),
            definition=json.dumps(result.get("definitions", {})),
            lineage=result.get("lineage"),
            role=persona,
            latency_ms=result.get("latency_ms"),
            row_count=result.get("row_count", 0),
        )
    except Exception as exc:
        return AnswerContract(error=str(exc))
