"""GOVERNED_QUERY: the only path from a question to a number.

Runs with caller's rights, so row access and masking apply to whoever asked. The
canonical form and hash come from ontology/semantic.py, the same module the API and
the evaluation suites import, so a hash means the same thing everywhere.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from typing import Any

from explain_lineage import lineage_for
from snowflake.snowpark import Session

import semantic
from snowflake import telemetry

STATEMENT_TIMEOUT_S = 30
ROW_CAP = 10_000
log = logging.getLogger("scm.governed_query")


VIEW_NAME = re.compile(r"^(SCM_GOVERNED|PLANNING_SV|PROCUREMENT_SV|LOGISTICS_SV|EXECUTIVE_SV)_V[0-9]{1,3}$")


def _declared(session: Session, kind: str, qualified: str) -> set[str]:
    # SHOW takes no bind variables; the view name is checked against VIEW_NAME before it gets here.
    rows = session.sql(f"SHOW SEMANTIC {kind} IN {qualified}").collect()
    return {r["name"].lower() for r in rows}


def run(session: Session, view: str, query: str, question: str = "", db: str | None = None) -> dict[str, Any]:
    # One JSON string rather than ARRAY and OBJECT arguments: agent procedure tools on a warehouse
    # accept only scalar argument types.
    started = time.perf_counter()
    # A session opened by agent:run from inside SPCS has no current database, so the DDL passes its own.
    db = db or session.get_current_database().strip('"')
    view = (view or "").strip().upper()
    if not VIEW_NAME.match(view):
        _audit(session, db, question, None, None, None, None, 0, started, refusal="unknown_view")
        return {"error": "unknown_view", "message": "not a governed semantic view"}
    qualified = f"{db}.SEMANTIC.{view}"
    registry = semantic.load_registry(semantic.REGISTRY_PATH)
    telemetry.set_span_attribute("scm.view", view)

    try:
        try:
            request = json.loads(query or "{}")
        except ValueError as exc:
            raise semantic.SemanticError("bad_query", "QUERY must be a JSON object") from exc
        if not isinstance(request, dict):
            raise semantic.SemanticError("bad_query", "QUERY must be a JSON object")
        filters = request.get("filters") or []
        canonical = semantic.canonicalise(registry, {
            "metrics": request.get("metrics") or [], "dimensions": request.get("dimensions") or [],
            "time": request.get("time") or request.get("time_window") or {},
            "filters": [{"dimension": f.get("dimension"), "operator": f.get("operator", "="),
                         "value": f.get("values", f.get("value"))} for f in filters if isinstance(f, dict)]})
        declared_metrics = _declared(session, "METRICS", qualified)
        declared_dims = _declared(session, "DIMENSIONS", qualified) | {semantic.PERIOD}
        missing = [m for m in canonical["metrics"] if m not in declared_metrics]
        if missing:
            raise semantic.SemanticError("unknown_metrics", f"{view} does not expose {', '.join(missing)}",
                                         suggestions={m: semantic.closest(m, sorted(declared_metrics)) for m in missing})
        missing = [d for d in canonical["dimensions"] if d not in declared_dims]
        if missing:
            raise semantic.SemanticError("unknown_dimensions", f"{view} does not expose {', '.join(missing)}",
                                         valid_dimensions=sorted(declared_dims))
    except semantic.SemanticError as exc:
        _audit(session, db, question, None, None, None, None, 0, started, refusal=exc.code)
        return exc.as_dict()

    digest = semantic.query_hash(canonical)
    sql = semantic.render_semantic_sql(registry, canonical, qualified)
    telemetry.set_span_attribute("scm.semantic_query_hash", digest)
    session.sql(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {STATEMENT_TIMEOUT_S}").collect()
    try:
        frame = session.sql(f"{sql}\nLIMIT {ROW_CAP + 1}").collect()
    except Exception as exc:
        _audit(session, db, question, canonical, digest, sql, None, 0, started, refusal="query_failed")
        log.error("governed_query_failed", extra={"hash": digest})
        return {"error": "query_failed", "message": f"The semantic view rejected the query: {exc.__class__.__name__}",
                "sql": sql}
    rows = [{k.lower(): semantic.governed_value(v) for k, v in r.as_dict().items()} for r in frame]
    truncated = len(rows) > ROW_CAP
    rows = rows[:ROW_CAP]
    checksum = hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()[:16]
    latency_ms = _audit(session, db, question, canonical, digest, sql, checksum, len(rows), started)

    metric_cards = []
    for name in canonical["metrics"]:
        m = registry.metrics[name]
        metric_cards.append({k: m[k] for k in ("name", "title", "definition", "formula_text", "version", "status",
                                                "grain", "date_basis", "window", "denominator", "unit", "owner",
                                                "steward", "parent")})
    log.info("governed_query_answered", extra={"hash": digest, "rows": len(rows), "latency_ms": latency_ms})
    return {
        "metric_name": ", ".join(canonical["metrics"]), "metrics": metric_cards,
        "definition": " ".join(c["definition"] for c in metric_cards), "canonical_query": canonical,
        "semantic_query_hash": digest, "sql": sql, "view": view, "engine": "snowflake",
        "lineage": lineage_for(session, registry, canonical["metrics"][0], db),
        "role": session.get_current_role().strip('"'), "user": session.sql("SELECT CURRENT_USER()").collect()[0][0],
        "rows": rows, "row_count": len(rows), "truncated": truncated, "result_checksum": checksum,
        "latency_ms": latency_ms, "notes": [], "request_id": session.query_tag or "",
    }


def _audit(session, db, question, canonical, digest, sql, checksum, row_count, started, refusal=None) -> int:
    latency_ms = int((time.perf_counter() - started) * 1000)
    # One JSON payload: a None bound on its own reaches PARSE_JSON as the text "None", and a
    # refusal must never fail to be recorded.
    payload = json.dumps({
        "question": question or None, "metrics": ", ".join(canonical["metrics"]) if canonical else None,
        "canonical": canonical, "hash": digest, "sql": sql, "checksum": checksum, "rows": row_count,
        "latency_ms": latency_ms, "refusal": refusal,
    })
    session.sql(
        f"INSERT INTO {db}.AUDIT.ANSWERS (ts, username, role_used, question, metric_names, canonical_query,"
        " semantic_query_hash, sql_executed, result_checksum, row_count, latency_ms, refusal, path)"
        " SELECT CURRENT_TIMESTAMP(), CURRENT_USER(), CURRENT_ROLE(), p:question::STRING, p:metrics::STRING,"
        " NULLIF(p:canonical, PARSE_JSON('null')), p:hash::STRING, p:sql::STRING, p:checksum::STRING,"
        " p:rows::NUMBER, p:latency_ms::NUMBER, p:refusal::STRING,"
        " COALESCE(TRY_PARSE_JSON(CURRENT_QUERY_TAG()):path::STRING, 'procedure')"
        " FROM (SELECT PARSE_JSON(?) AS p)",
        params=[payload],
    ).collect()
    return latency_ms
