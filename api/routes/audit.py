"""GET /audit — recent entries from AUDIT.ANSWERS."""

from __future__ import annotations

from fastapi import APIRouter

from ..snowflake_client import get_connection

router = APIRouter()


@router.get("/audit")
async def get_audit(limit: int = 50):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT ts, username, role_used, semantic_query_hash, latency_ms
            FROM AUDIT.ANSWERS
            ORDER BY ts DESC
            LIMIT {min(limit, 200)}
        """)
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "ts": str(row[0]),
                "username": row[1],
                "role": row[2],
                "hash": row[3],
                "latency_ms": row[4],
            }
            for row in rows
        ]
    except Exception as exc:
        return {"error": str(exc)}
