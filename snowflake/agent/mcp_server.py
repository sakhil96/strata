"""MCP server exposing the three governed procedures.

Locally it answers from the DuckDB build through the same backend the API uses; with
SCM_BACKEND=snowflake it calls the procedures under the configured connection's role.
Run: python snowflake/agent/mcp_server.py  (stdio transport).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from api.backend import Caller, get_backend  # noqa: E402

server = FastMCP("strata-governed")
ROLE = os.getenv("SCM_MCP_ROLE", "EXECUTIVE_ROLE")


def _caller() -> Caller:
    return Caller(os.getenv("SCM_MCP_USER", "MCP_CLIENT"), ROLE, "mcp")


@server.tool()
def governed_query(metrics: list[str], dimensions: list[str] | None = None, time_range: str = "fy2026",
                   filters: list[dict[str, Any]] | None = None, question: str = "") -> dict[str, Any]:
    """Run a governed metric query; returns rows, definition, canonical query, hash, SQL and lineage."""
    try:
        return get_backend().query(_caller(), {"metrics": metrics, "dimensions": dimensions or [],
                                               "time": {"range": time_range}, "filters": filters or []}, question)
    except ValueError as exc:
        return exc.as_dict() if hasattr(exc, "as_dict") else {"error": str(exc)}


@server.tool()
def describe_metric(name: str) -> dict[str, Any]:
    """Return the governed definition, owner, steward, version and variants of one metric."""
    registry = get_backend().registry
    metric = registry.metrics.get(name.strip().lower())
    if not metric:
        from semantic import closest

        return {"error": "unknown_metrics", "suggestions": {name: closest(name, list(registry.metrics))}}
    return {k: metric[k] for k in ("name", "title", "definition", "formula_text", "owner", "steward", "version",
                                   "status", "unit", "grain", "date_basis", "parent", "variants")}


@server.tool()
def explain_lineage(metric: str) -> dict[str, Any]:
    """Return the path from source files to the semantic-view metric."""
    try:
        return get_backend().lineage(metric.strip().lower())
    except ValueError as exc:
        return exc.as_dict() if hasattr(exc, "as_dict") else {"error": str(exc)}


if __name__ == "__main__":
    server.run()
