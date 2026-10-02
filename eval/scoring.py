from __future__ import annotations

from typing import Any

import resolver
import semantic


def dimension_values(connection) -> dict[str, list[str]]:
    def distinct(sql: str) -> list[str]:
        return sorted(r[0] for r in connection.execute(sql).fetchall())

    return {
        "segment": distinct("select distinct segment from conformed.dim_customer"),
        "part_family": distinct("select distinct part_family from conformed.dim_part"),
        "category": distinct("select distinct category from conformed.dim_part"),
        "region": distinct("select distinct region from conformed.dim_plant"),
    }


def score_item(registry: semantic.Registry, item: dict[str, Any], resolution: dict[str, Any]) -> dict[str, Any]:
    if item["scope"] == "out_of_scope":
        return {"id": item["id"], "refused": resolution.get("refusal") is not None,
                "metric_resolved": None, "exact_query": None}
    query = resolution.get("query")
    if not query:
        return {"id": item["id"], "refused": True, "metric_resolved": False, "exact_query": False}
    expected = semantic.canonicalise(registry, item["query"])
    try:
        got = semantic.canonicalise(registry, query)
    except semantic.SemanticError:
        return {"id": item["id"], "refused": False, "metric_resolved": False, "exact_query": False}
    return {"id": item["id"], "refused": False,
            "metric_resolved": got["metrics"] == expected["metrics"],
            "exact_query": got == expected,
            "expected_hash": semantic.query_hash(expected), "hash": semantic.query_hash(got)}


def resolve_locally(registry, values, item, persona=None) -> dict[str, Any]:
    return resolver.resolve(registry, item["question"], persona, values).as_dict()
