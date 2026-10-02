"""GET /meta — API metadata."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/meta")
async def get_meta():
    return {
        "name": "STRATA",
        "version": "0.1.0",
        "description": "Governed supply chain ontology API",
        "endpoints": [
            {"path": "/api/ask", "method": "POST", "description": "Natural language question through the agent"},
            {"path": "/api/query", "method": "POST", "description": "Structured governed query (no model)"},
            {"path": "/api/glossary", "method": "GET", "description": "Metric glossary"},
            {"path": "/api/lineage/{metric}", "method": "GET", "description": "Metric lineage"},
            {"path": "/api/compare", "method": "POST", "description": "Cross-persona comparison"},
            {"path": "/api/before-after", "method": "POST", "description": "Before/after metric comparison"},
            {"path": "/api/audit", "method": "GET", "description": "Recent audit entries"},
            {"path": "/api/eval/report", "method": "GET", "description": "Latest evaluation report"},
            {"path": "/health", "method": "GET", "description": "Readiness probe"},
            {"path": "/live", "method": "GET", "description": "Liveness probe"},
        ],
    }
