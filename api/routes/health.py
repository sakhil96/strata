"""Health and liveness probes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def readiness():
    """Readiness probe — returns 200 when the service can accept requests."""
    return {"status": "ready", "service": "strata"}


@router.get("/live")
async def liveness():
    """Liveness probe — returns 200 when the process is alive."""
    return {"status": "alive"}
