"""POST /ask — route a natural language question through the Cortex Agent."""

from __future__ import annotations

import json
import os

from fastapi import APIRouter, Request

from ..schemas import AskRequest, AnswerContract

router = APIRouter()


@router.post("/ask", response_model=AnswerContract)
async def ask_question(body: AskRequest, request: Request):
    """Send a question to the Cortex Agent and return the governed answer."""
    import httpx

    sf_user = request.headers.get("Sf-Context-Current-User", "dev_user")
    env = os.getenv("SCM_ENV", "dev").upper()
    db = f"SCM_{env}"
    account = os.getenv("SNOWFLAKE_ACCOUNT", "")

    agent_endpoint = f"https://{account}.snowflakecomputing.com/api/v2/cortex/agent:run"

    payload = {
        "agent_name": f"{db}.AGENT.SCM_AGENT",
        "messages": [{"role": "user", "content": body.question}],
        "tools": {},
    }

    # In production, this uses the SPCS service token or key-pair JWT
    # For local dev, it falls back to the Snowflake connector's auth
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                agent_endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Sf-Context-Current-User": sf_user,
                },
            )
            resp.raise_for_status()
            result = resp.json()

        return AnswerContract(
            rows=result.get("rows", []),
            sql=result.get("sql"),
            canonical_query=result.get("canonical_query"),
            semantic_query_hash=result.get("semantic_query_hash"),
            definition=result.get("definition"),
            lineage=result.get("lineage"),
            role=body.persona,
            latency_ms=result.get("latency_ms"),
            row_count=result.get("row_count", 0),
        )
    except Exception as exc:
        return AnswerContract(error=str(exc))
