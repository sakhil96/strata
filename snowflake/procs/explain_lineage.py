"""EXPLAIN_LINEAGE: source to semantic view for one metric, from Snowflake's own lineage graph."""

from __future__ import annotations

from typing import Any

import semantic
from snowflake.snowpark import Session

LAYERS = (("RAW", "source"), ("STAGING", "staging"), ("CONFORMED", "conformed"))


def lineage_for(session: Session, registry: semantic.Registry, metric: str) -> dict[str, Any]:
    m = registry.metrics[metric]
    table = m["semantic"]["table"]
    db = session.get_current_database().strip('"')
    base = f"{db}.CONFORMED.{registry.tables[table]['base_table']}"
    edges = session.sql(
        "SELECT source_object_schema, source_object_name, target_object_schema, target_object_name, distance "
        "FROM TABLE(SNOWFLAKE.CORE.GET_LINEAGE(?, 'TABLE', 'UPSTREAM', 5))", params=[base]).collect()
    layers: dict[str, set[str]] = {name: set() for _, name in LAYERS}
    layers["conformed"].add(registry.tables[table]["base_table"].lower())
    for e in edges:
        for schema, name in ((e[0], e[1]), (e[2], e[3])):
            for prefix, layer in LAYERS:
                if schema == prefix:
                    layers[layer].add(name.lower())
    facts = sorted(f for f in registry.tables[table].get("facts", []) if f"{table}.{f}" in m["semantic"]["expr"])
    return {
        "metric": metric, "source": "Snowflake lineage graph" if edges else "registry (lineage graph empty)",
        "expression": m["semantic"]["expr"],
        "path": [{"layer": layer, "objects": sorted(objs)} for layer, objs in layers.items()]
        + [{"layer": "semantic", "objects": [f"{table}.{metric}"], "columns": facts}],
    }


def run(session: Session, metric: str) -> dict[str, Any]:
    registry = semantic.load_registry(semantic.REGISTRY_PATH)
    name = (metric or "").strip().lower()
    if name not in registry.metrics:
        return {"error": "unknown_metrics", "message": f"{metric!r} is not a governed metric",
                "suggestions": {metric: semantic.closest(name, list(registry.metrics))}}
    return lineage_for(session, registry, name)
