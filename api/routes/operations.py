from __future__ import annotations

import json

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from ..backend import ROOT
from .deps import backend, caller

router = APIRouter(tags=["operations"])
GOVERNANCE = ROOT / "eval" / "governance_snapshot.json"


@router.get("/audit", summary="Most recent governed answers and refusals")
def audit(request: Request, limit: int = Query(default=50, ge=1, le=200)):
    caller(request)
    return backend().audit(limit)


@router.get("/eval/report", summary="Latest evaluation report")
def eval_report(request: Request):
    caller(request)
    report = backend().eval_report()
    if report is None:
        return JSONResponse(status_code=404, content={"error": "no_report", "message": "Run `make eval` to produce one."})
    return report


@router.get("/governance", summary="The deployed agent's tools, and the grants and policies the setup makes")
def governance(request: Request):
    caller(request)
    if not GOVERNANCE.exists():
        return JSONResponse(status_code=404, content={"error": "no_snapshot", "message": "Run `make governance-snapshot`."})
    return {**json.loads(GOVERNANCE.read_text()), "agent": backend().agent_card()}


@router.get("/status", summary="Freshness, last dbt run and last evaluation score")
def status(request: Request):
    caller(request)
    return backend().status()


@router.get("/operations", summary="Service levels, alerts and this week's cost")
def operations(request: Request):
    caller(request)
    return backend().operations()
