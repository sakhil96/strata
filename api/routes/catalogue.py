from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ..backend import ROOT, VERSION
from .deps import backend, caller

router = APIRouter(tags=["catalogue"])
GLOSSARY = ROOT / "ontology" / "generated" / "glossary.json"


def glossary_entries() -> list[dict]:
    return json.loads(GLOSSARY.read_text())


@router.get("/meta", summary="Metrics, dimensions and windows the Builder can offer")
def meta(request: Request):
    caller(request)
    registry = backend().registry
    dims = {}
    for table, spec in registry.tables.items():
        for d in spec.get("dimensions", {}):
            dims[d] = {"table": table, "title": spec["dimensions"][d].get("title", d), "synonyms": spec["dimensions"][d].get("synonyms", [])}
    return {
        "version": VERSION,
        "metrics": [{"name": n, "title": m["title"], "type": m["type"], "unit": m["unit"], "parent": m["parent"],
                     "date_basis": m["date_basis"], "dimensions": sorted(registry.reachable(m["semantic"]["table"]))}
                    for n, m in sorted(registry.metrics.items())],
        "dimensions": dims,
        "windows": ["fy2026", "q1", "q2", "q3", "q4", "last_quarter", "last_month", "across_tariff_step", "pre_tariff_step",
                    "post_tariff_step"],
        "values": backend().dimension_values() if hasattr(backend(), "dimension_values") else {},
    }


@router.get("/glossary", summary="Every governed metric and variant with its definition and steward")
def glossary(request: Request):
    caller(request)
    return glossary_entries()


@router.get("/lineage/{metric}", summary="Source to semantic-view path for one metric")
def lineage(metric: str, request: Request):
    caller(request)
    try:
        return backend().lineage(metric.lower())
    except ValueError as exc:
        return JSONResponse(status_code=404, content=exc.as_dict() if hasattr(exc, "as_dict") else {"error": str(exc)})
