"""GOVERNED_QUERY — the single path through which all metric questions are answered.

Caller's rights procedure. Validates inputs against semantic metadata, builds
SEMANTIC_VIEW() SQL, executes with timeout and row cap, writes to AUDIT.ANSWERS,
emits telemetry, and returns the full answer contract.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime

import _snowflake
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col


STATEMENT_TIMEOUT_MS = 30_000
ROW_CAP = 10_000


def governed_query(
    session: Session,
    view: str,
    metrics: list[str],
    dimensions: list[str],
    time_spec: dict,
    filters: list[dict],
) -> dict:
    """Execute a governed metric query through a semantic view.

    Returns the full answer contract: rows, sql, hash, definition, lineage.
    """
    start_ts = time.time()
    user = session.sql("SELECT CURRENT_USER()").collect()[0][0]
    role = session.sql("SELECT CURRENT_ROLE()").collect()[0][0]
    db = session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]

    # Validate metrics exist in the semantic view
    valid_metrics = _get_valid_metrics(session, db, view)
    valid_dimensions = _get_valid_dimensions(session, db, view)

    unknown_metrics = [m for m in metrics if m.upper() not in {v.upper() for v in valid_metrics}]
    if unknown_metrics:
        closest = {m: _closest_match(m, valid_metrics) for m in unknown_metrics}
        return {
            "error": "unknown_metrics",
            "unknown": unknown_metrics,
            "suggestions": closest,
            "valid_metrics": valid_metrics,
        }

    unknown_dims = [d for d in dimensions if d.upper() not in {v.upper() for v in valid_dimensions}]
    if unknown_dims:
        closest = {d: _closest_match(d, valid_dimensions) for d in unknown_dims}
        return {
            "error": "unknown_dimensions",
            "unknown": unknown_dims,
            "suggestions": closest,
            "valid_dimensions": valid_dimensions,
        }

    # Canonicalise the query
    canonical = _canonicalise(metrics, dimensions, time_spec, filters)
    canonical_json = json.dumps(canonical, sort_keys=True)
    query_hash = hashlib.sha256(canonical_json.encode()).hexdigest()[:16]

    # Build SEMANTIC_VIEW() SQL
    metrics_clause = ", ".join(metrics)
    dims_clause = ", ".join(dimensions) if dimensions else ""
    where_parts = _build_where(time_spec, filters)

    sv_ref = f"{db}.SEMANTIC.{view}"
    sql_parts = [f"SELECT * FROM SEMANTIC_VIEW('{sv_ref}'"]
    sql_parts.append(f"  METRICS {metrics_clause}")
    if dims_clause:
        sql_parts.append(f"  DIMENSIONS {dims_clause}")
    if where_parts:
        sql_parts.append(f"  WHERE {' AND '.join(where_parts)}")
    sql_parts.append(")")
    if dimensions:
        sql_parts.append(f"ORDER BY {dims_clause}")
    sql_parts.append(f"LIMIT {ROW_CAP}")

    semantic_sql = "\n".join(sql_parts)

    # Execute with timeout
    try:
        session.sql(f"ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = {STATEMENT_TIMEOUT_MS // 1000}").collect()
        result_df = session.sql(semantic_sql)
        rows = result_df.to_pandas().to_dict(orient="records")
    except Exception as exc:
        _write_audit(session, db, user, role, "", canonical_json, query_hash, semantic_sql, str(exc), 0, start_ts)
        return {"error": "query_failed", "message": str(exc), "sql": semantic_sql}

    # Fetch definitions from glossary
    definitions = _get_definitions(session, db, metrics)

    # Fetch lineage
    lineage = _get_lineage(session, db, metrics)

    latency_ms = int((time.time() - start_ts) * 1000)
    result_checksum = hashlib.sha256(json.dumps(rows, default=str).encode()).hexdigest()[:16]

    # Write audit record
    _write_audit(session, db, user, role, "", canonical_json, query_hash, semantic_sql, result_checksum, len(rows), start_ts)

    # Emit telemetry
    _log_event(session, "governed_query", {
        "user": user, "role": role, "metrics": metrics, "hash": query_hash, "latency_ms": latency_ms,
    })

    return {
        "rows": rows,
        "sql": semantic_sql,
        "canonical_query": canonical,
        "semantic_query_hash": query_hash,
        "definitions": definitions,
        "lineage": lineage,
        "role": role,
        "latency_ms": latency_ms,
        "row_count": len(rows),
    }


def _get_valid_metrics(session: Session, db: str, view: str) -> list[str]:
    try:
        df = session.sql(f"SHOW SEMANTIC METRICS IN SEMANTIC VIEW {db}.SEMANTIC.{view}")
        return [row[0] for row in df.collect()]
    except Exception:
        return []


def _get_valid_dimensions(session: Session, db: str, view: str) -> list[str]:
    try:
        df = session.sql(f"SHOW SEMANTIC DIMENSIONS IN SEMANTIC VIEW {db}.SEMANTIC.{view}")
        return [row[0] for row in df.collect()]
    except Exception:
        return []


def _closest_match(name: str, candidates: list[str]) -> list[str]:
    name_lower = name.lower()
    scored = [(c, _edit_distance(name_lower, c.lower())) for c in candidates]
    scored.sort(key=lambda x: x[1])
    return [c for c, _ in scored[:3]]


def _edit_distance(a: str, b: str) -> int:
    if len(a) < len(b):
        return _edit_distance(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def _canonicalise(
    metrics: list[str],
    dimensions: list[str],
    time_spec: dict,
    filters: list[dict],
) -> dict:
    return {
        "metrics": sorted([m.lower() for m in metrics]),
        "dimensions": sorted([d.lower() for d in dimensions]),
        "time": {k: str(v) for k, v in sorted(time_spec.items())},
        "filters": sorted([{k: str(v) for k, v in f.items()} for f in filters], key=lambda x: json.dumps(x, sort_keys=True)),
    }


def _build_where(time_spec: dict, filters: list[dict]) -> list[str]:
    parts = []
    if "start" in time_spec and "end" in time_spec:
        date_col = time_spec.get("date_column", "date")
        parts.append(f"{date_col} BETWEEN '{time_spec['start']}' AND '{time_spec['end']}'")
    for f in filters:
        col_name = f.get("column", "")
        op = f.get("operator", "=")
        val = f.get("value", "")
        if col_name and val:
            if op.upper() == "IN":
                vals = ", ".join(f"'{v}'" for v in val) if isinstance(val, list) else f"'{val}'"
                parts.append(f"{col_name} IN ({vals})")
            else:
                parts.append(f"{col_name} {op} '{val}'")
    return parts


def _get_definitions(session: Session, db: str, metrics: list[str]) -> dict:
    defs = {}
    try:
        for m in metrics:
            df = session.sql(
                f"SELECT definition, formula_text, owner, steward, version "
                f"FROM {db}.SEMANTIC.GLOSSARY WHERE metric_name = '{m.lower()}'"
            )
            rows = df.collect()
            if rows:
                defs[m] = {
                    "definition": rows[0][0],
                    "formula_text": rows[0][1],
                    "owner": rows[0][2],
                    "steward": rows[0][3],
                    "version": rows[0][4],
                }
    except Exception:
        pass
    return defs


def _get_lineage(session: Session, db: str, metrics: list[str]) -> dict:
    lineage = {}
    try:
        for m in metrics:
            df = session.sql(
                f"SELECT * FROM TABLE(GET_LINEAGE('{db}.SEMANTIC.SCM_GOVERNED', 'SEMANTIC_VIEW'))"
            )
            rows = df.collect()
            if rows:
                lineage[m] = [str(row) for row in rows[:5]]
    except Exception:
        pass
    return lineage


def _write_audit(
    session: Session, db: str, user: str, role: str,
    question: str, canonical_json: str, query_hash: str,
    sql: str, result_checksum: str, row_count: int, start_ts: float,
) -> None:
    latency_ms = int((time.time() - start_ts) * 1000)
    try:
        session.sql(f"""
            CREATE TABLE IF NOT EXISTS {db}.AUDIT.ANSWERS (
                ts TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                username STRING,
                role_used STRING,
                question STRING,
                canonical_query STRING,
                semantic_query_hash STRING,
                sql_executed STRING,
                result_checksum STRING,
                row_count INTEGER,
                latency_ms INTEGER
            )
        """).collect()
        session.sql(f"""
            INSERT INTO {db}.AUDIT.ANSWERS
            (username, role_used, question, canonical_query, semantic_query_hash, sql_executed, result_checksum, row_count, latency_ms)
            VALUES ('{user}', '{role}', '{question}', $${canonical_json}$$, '{query_hash}', $${sql}$$, '{result_checksum}', {row_count}, {latency_ms})
        """).collect()
    except Exception:
        pass


def _log_event(session: Session, event_name: str, attributes: dict) -> None:
    import logging
    logger = logging.getLogger("scm.governed_query")
    logger.info(event_name, extra={"attributes": attributes})
