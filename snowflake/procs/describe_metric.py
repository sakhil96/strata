"""DESCRIBE_METRIC: the governed definition of one metric, read from SEMANTIC.GLOSSARY."""

from __future__ import annotations

from typing import Any

import semantic
from snowflake.snowpark import Session


def run(session: Session, name: str) -> dict[str, Any]:
    db = session.get_current_database().strip('"')
    rows = session.sql(f"SELECT entry FROM {db}.SEMANTIC.GLOSSARY WHERE metric_name = ?",
                       params=[(name or "").strip().lower()]).collect()
    if rows:
        import json

        return json.loads(rows[0]["ENTRY"])
    known = [r["METRIC_NAME"] for r in session.sql(f"SELECT metric_name FROM {db}.SEMANTIC.GLOSSARY").collect()]
    return {"error": "unknown_metrics", "message": f"{name!r} is not a governed metric",
            "suggestions": {name: semantic.closest(name or "", known)}}
