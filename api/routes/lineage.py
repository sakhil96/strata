"""GET /lineage/{metric} — metric lineage from EXPLAIN_LINEAGE."""

from __future__ import annotations

from fastapi import APIRouter

from ..snowflake_client import get_connection, execute_procedure

router = APIRouter()


@router.get("/lineage/{metric}")
async def get_lineage(metric: str):
    try:
        conn = get_connection()
        result = execute_procedure(conn, "EXPLAIN_LINEAGE", metric)
        conn.close()
        return result
    except Exception as exc:
        return {"error": str(exc)}
