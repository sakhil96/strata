"""Semantic queries over the registry's model: canonical form, hash, SQL, local execution.

GOVERNED_QUERY imports this module on Snowflake; the API, the evaluation suites and
the local demo import it directly. One implementation means one hash.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path(__file__).resolve().parent / "metrics.yaml"
FY_START = date(2025, 10, 1)
# The July 2026 tariff step: across_tariff_step spans three months either side, July itself the step month.
TARIFF_STEP = date(2026, 7, 24)
AS_OF = date(2026, 9, 30)
PERIOD = "period_month"
INHERITED = (
    "title", "type", "grain", "date_basis", "window", "numerator", "denominator", "definition",
    "formula_text", "synonyms", "owner", "steward", "scor_attribute", "unit", "persona_synonyms",
    "version", "status", "approved_by", "approved_on",
)
REQUIRED = (*INHERITED, "variants", "semantic")
LITERAL = re.compile(r"^[A-Za-z0-9 _.,&'()/\-]{1,80}$")
OPERATORS = {"=", "!=", "in"}


class SemanticError(ValueError):
    def __init__(self, code: str, message: str, **detail: Any):
        super().__init__(message)
        self.code = code
        self.detail = detail

    def as_dict(self) -> dict[str, Any]:
        return {"error": self.code, "message": str(self), **self.detail}


@dataclass(frozen=True)
class Registry:
    constants: dict[str, Any]
    tables: dict[str, dict[str, Any]]
    metrics: dict[str, dict[str, Any]]

    @property
    def dimensions(self) -> dict[str, str]:
        owners = {}
        for table, spec in self.tables.items():
            for name in spec.get("dimensions", {}):
                owners[name] = table
        return owners

    def reachable(self, fact_table: str) -> set[str]:
        keys = self.tables[fact_table].get("keys", {})
        names = {PERIOD}
        for dim_table in keys.values():
            names.update(self.tables[dim_table].get("dimensions", {}))
        return names


def load_registry(path: Path = REGISTRY_PATH) -> Registry:
    raw = yaml.safe_load(path.read_text())
    return Registry(raw["constants"], raw["model"]["tables"], flatten_metrics(raw["metrics"]))


def flatten_metrics(metrics: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    flat: dict[str, dict[str, Any]] = {}
    for name, spec in metrics.items():
        missing = [f for f in REQUIRED if spec.get(f) is None]
        if missing:
            raise SemanticError("registry_incomplete", f"metric {name} is missing {', '.join(missing)}",
                                metric=name, missing=missing)
        parent = {k: copy.deepcopy(v) for k, v in spec.items() if k != "variants"}
        parent.update(name=name, parent=None, variants=sorted(spec["variants"]))
        flat[name] = parent
        for variant, override in spec["variants"].items():
            if variant in metrics or variant in flat:
                raise SemanticError("registry_duplicate", f"variant {variant} collides with a metric")
            child = {k: copy.deepcopy(spec[k]) for k in INHERITED}
            child.update(copy.deepcopy(override))
            child.update(name=variant, parent=name, variants=[])
            if "semantic" not in override:
                raise SemanticError("registry_incomplete", f"variant {variant} has no semantic expression")
            flat[variant] = child
    return flat


def fiscal_range(label: str) -> tuple[date, date]:
    label = label.lower().replace(" ", "")
    quarters = {
        "q1": (date(2025, 10, 1), date(2025, 12, 1)), "q2": (date(2026, 1, 1), date(2026, 3, 1)),
        "q3": (date(2026, 4, 1), date(2026, 6, 1)), "q4": (date(2026, 7, 1), date(2026, 9, 1)),
    }
    if label in ("fy2026", "fytd", "this_year", "year"):
        return FY_START, date(AS_OF.year, AS_OF.month, 1)
    if label in quarters:
        return quarters[label]
    if label in ("last_quarter", "this_quarter"):
        return quarters["q4"]
    if label == "last_month":
        return date(AS_OF.year, AS_OF.month, 1), date(AS_OF.year, AS_OF.month, 1)
    if label == "across_tariff_step":
        return date(2026, 4, 1), date(2026, 9, 1)
    if label == "pre_tariff_step":
        return date(2026, 4, 1), date(2026, 6, 1)
    if label == "post_tariff_step":
        return date(2026, 8, 1), date(2026, 9, 1)
    raise SemanticError("unknown_time_range", f"time range {label!r} is not one we resolve",
                        valid=sorted([*quarters, "fy2026", "last_quarter", "last_month",
                                      "across_tariff_step", "pre_tariff_step", "post_tariff_step"]))


def _month(text: str) -> date:
    try:
        d = date.fromisoformat(str(text)[:10])
    except ValueError as exc:
        raise SemanticError("bad_date", f"{text!r} is not an ISO date") from exc
    return date(d.year, d.month, 1)


def closest(name: str, candidates: list[str]) -> list[str]:
    def distance(a: str, b: str) -> int:
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i]
            for j, cb in enumerate(b, 1):
                cur.append(min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
            prev = cur
        return prev[-1]

    return sorted(candidates, key=lambda c: (distance(name.lower(), c.lower()), c))[:3]


def canonicalise(registry: Registry, query: dict[str, Any]) -> dict[str, Any]:
    metrics = sorted({str(m).strip().lower() for m in query.get("metrics", [])})
    if not metrics:
        raise SemanticError("no_metrics", "name at least one metric")
    unknown = [m for m in metrics if m not in registry.metrics]
    if unknown:
        raise SemanticError("unknown_metrics", f"not governed metrics: {', '.join(unknown)}",
                            unknown=unknown,
                            suggestions={m: closest(m, list(registry.metrics)) for m in unknown})
    tables = sorted({registry.metrics[m]["semantic"]["table"] for m in metrics})

    dimensions = sorted({str(d).strip().lower() for d in query.get("dimensions", [])})
    shared = set.intersection(*(registry.reachable(t) for t in tables))
    unknown = [d for d in dimensions if d not in shared]
    if unknown:
        valid = sorted(shared)
        raise SemanticError("unknown_dimensions",
                            f"not available for {', '.join(metrics)}: {', '.join(unknown)}",
                            unknown=unknown, valid_dimensions=valid,
                            suggestions={d: closest(d, valid) for d in unknown})
    if PERIOD in dimensions and len(tables) > 1:
        raise SemanticError("mixed_date_basis",
                            "these metrics are dated on different bases; ask for them by month separately",
                            metrics=metrics)

    time = query.get("time") or {}
    if time.get("range"):
        start, end = fiscal_range(time["range"])
    else:
        start = _month(time.get("start", FY_START))
        end = _month(time.get("end", AS_OF))
    if start > end:
        raise SemanticError("bad_time_window", "the window starts after it ends")

    filters = []
    for f in query.get("filters", []) or []:
        dim = str(f.get("dimension", "")).lower()
        op = str(f.get("operator", "=")).lower()
        if dim not in shared or dim == PERIOD:
            raise SemanticError("unknown_dimensions", f"cannot filter on {dim!r}",
                                unknown=[dim], valid_dimensions=sorted(shared - {PERIOD}))
        if op not in OPERATORS:
            raise SemanticError("bad_operator", f"operator {op!r} is not one of =, !=, in")
        values = f.get("value")
        values = sorted({str(v) for v in values}) if isinstance(values, list) else [str(values)]
        for v in values:
            if not LITERAL.match(v):
                raise SemanticError("bad_filter_value", f"filter value {v!r} has characters we do not accept")
        filters.append({"dimension": dim, "operator": op, "values": values})
    filters.sort(key=lambda f: (f["dimension"], f["operator"], f["values"]))

    return {
        "metrics": metrics,
        "dimensions": dimensions,
        "time": {"start": start.isoformat(), "end": end.isoformat()},
        "filters": filters,
    }


def query_hash(canonical: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _qualify(registry: Registry, name: str, fact_table: str) -> str:
    return f"{fact_table}.{PERIOD}" if name == PERIOD else f"{registry.dimensions[name]}.{name}"


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def render_semantic_sql(registry: Registry, canonical: dict[str, Any], view: str) -> str:
    tables = sorted({registry.metrics[m]["semantic"]["table"] for m in canonical["metrics"]})
    anchor = tables[0]
    lines = ["SELECT * FROM SEMANTIC_VIEW(", f"    {view}"]
    if canonical["dimensions"]:
        lines.append("    DIMENSIONS " + ", ".join(_qualify(registry, d, anchor) for d in canonical["dimensions"]))
    lines.append("    METRICS " + ", ".join(
        f"{registry.metrics[m]['semantic']['table']}.{m}" for m in canonical["metrics"]))
    where = []
    for t in tables:
        # A position (NON ADDITIVE BY period_month) asked for without a month breakdown reads the
        # window's closing month. That is pinned here rather than left to the view's own
        # "latest period" choice, which on the account returned the earliest month instead.
        if registry.tables[t].get("non_additive_by") == PERIOD and PERIOD not in canonical["dimensions"]:
            where.append(f"{t}.{PERIOD} = '{canonical['time']['end']}'")
        else:
            where.append(f"{t}.{PERIOD} BETWEEN '{canonical['time']['start']}' AND '{canonical['time']['end']}'")
    for f in canonical["filters"]:
        col = _qualify(registry, f["dimension"], anchor)
        if f["operator"] == "in":
            where.append(f"{col} IN ({', '.join(_literal(v) for v in f['values'])})")
        else:
            where.append(f"{col} {f['operator']} {_literal(f['values'][0])}")
    lines.append("    WHERE " + "\n      AND ".join(where))
    lines.append(")")
    if canonical["dimensions"]:
        lines.append("ORDER BY " + ", ".join(canonical["dimensions"]))
    return "\n".join(lines)


def _local_table_sql(registry: Registry, canonical: dict[str, Any], fact: str, metrics: list[str],
                     params: list[Any]) -> str:
    spec = registry.tables[fact]
    joins, needed = [], set()
    for d in canonical["dimensions"] + [f["dimension"] for f in canonical["filters"]]:
        if d != PERIOD:
            needed.add(registry.dimensions[d])
    for key, dim_table in sorted(spec.get("keys", {}).items()):
        if dim_table in needed:
            dim_spec = registry.tables[dim_table]
            joins.append(f"LEFT JOIN CONFORMED.{dim_spec['base_table']} AS {dim_table} "
                         f"ON {dim_table}.{dim_spec['primary_key'][0]} = {fact}.{key}")

    def col(name: str) -> str:
        return f"{fact}.{spec['period']}" if name == PERIOD else f"{registry.dimensions[name]}.{name}"

    where = [f"{fact}.{spec['period']} BETWEEN ? AND ?"]
    params.extend([canonical["time"]["start"], canonical["time"]["end"]])
    for f in canonical["filters"]:
        if f["operator"] == "in":
            where.append(f"{col(f['dimension'])} IN ({', '.join('?' for _ in f['values'])})")
            params.extend(f["values"])
        else:
            where.append(f"{col(f['dimension'])} {f['operator']} ?")
            params.append(f["values"][0])

    # NON ADDITIVE BY period_month: without a month dimension, inventory reads the window's closing
    # month, the same rule render_semantic_sql gives the semantic view.
    if spec.get("non_additive_by") == PERIOD and PERIOD not in canonical["dimensions"]:
        where.append(f"{fact}.{spec['period']} = ?")
        params.append(canonical["time"]["end"])

    select = [f"{col(d)} AS {d}" for d in canonical["dimensions"]]
    select += [f"{registry.metrics[m]['semantic']['expr']} AS {m}" for m in metrics]
    sql = (f"SELECT {', '.join(select)} FROM CONFORMED.{spec['base_table']} AS {fact} "
           f"{' '.join(joins)} WHERE {' AND '.join(where)}")
    if canonical["dimensions"]:
        sql += " GROUP BY " + ", ".join(col(d) for d in canonical["dimensions"])
    return sql


def local_sql(registry: Registry, canonical: dict[str, Any]) -> tuple[str, list[Any]]:
    by_table: dict[str, list[str]] = {}
    for m in canonical["metrics"]:
        by_table.setdefault(registry.metrics[m]["semantic"]["table"], []).append(m)
    params: list[Any] = []
    parts = [(t, _local_table_sql(registry, canonical, t, ms, params)) for t, ms in sorted(by_table.items())]
    dims = canonical["dimensions"]
    if len(parts) == 1:
        sql = parts[0][1]
    else:
        sql = f"SELECT * FROM ({parts[0][1]}) AS {parts[0][0]}_part"
        for table, part in parts[1:]:
            if dims:
                sql += f" FULL OUTER JOIN ({part}) AS {table}_part USING ({', '.join(dims)})"
            else:
                sql += f" CROSS JOIN ({part}) AS {table}_part"
    if dims:
        sql = f"SELECT * FROM ({sql}) AS answer ORDER BY {', '.join(dims)}"
    return sql, params


SIGNIFICANT = 12


def governed_value(value: Any) -> Any:
    """A float sum is not ordered, so the last digits of the same query can differ between runs and
    roles; a governed number is the value at 12 significant digits, in both engines."""
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) or (hasattr(value, "as_integer_ratio") and not isinstance(value, (int, bool))):
        return float(f"{float(value):.{SIGNIFICANT}g}")
    return value


def execute_local(connection: Any, registry: Registry, query: dict[str, Any]) -> dict[str, Any]:
    canonical = canonicalise(registry, query)
    sql, params = local_sql(registry, canonical)
    cursor = connection.execute(sql, params)
    columns = [c[0] for c in cursor.description]
    rows = [dict(zip(columns, (governed_value(v) for v in r), strict=False)) for r in cursor.fetchall()]
    return {"canonical_query": canonical, "semantic_query_hash": query_hash(canonical), "rows": rows}
