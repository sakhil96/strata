"""GET /eval/report — latest evaluation report."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

REPORT_PATH = Path(__file__).resolve().parent.parent.parent / "eval" / "report.json"


@router.get("/eval/report")
async def get_eval_report():
    if REPORT_PATH.exists():
        return json.loads(REPORT_PATH.read_text())
    return {"error": "no evaluation report found — run make eval first"}
