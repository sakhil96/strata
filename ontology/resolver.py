"""Resolve a question to a semantic query without a model.

This is the fallback path when the agent is unavailable and the baseline the agent is
scored against. It only ever produces governed metric names; anything it cannot place
is refused.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from semantic import PERIOD, Registry

INJECTION = re.compile(
    r"ignore (all |your |previous )*instructions|developer mode|system:|jailbreak|print your instructions"
    r"|reveal .*prompt|act as", re.I)
RAW_ACCESS = re.compile(
    r"\bselect\b.+\bfrom\b|\bdelete\b|\bdrop\b|\binsert\b|\bupdate\b|\btruncate\b|raw sql|table names?"
    r"|\bschema\b|connection string|which database|what database|\bgrant\b", re.I)
DIMENSION_WORDS = {
    "plant_id": ["plant", "site", "facility", "dc", "warehouse location"],
    "region": ["region", "geography", "theatre"],
    "segment": ["segment", "customer segment"],
    "part_family": ["family", "product family", "part family"],
    "category": ["category", "product category"],
    "supplier_name": ["supplier", "vendor"],
    "supplier_country": ["supplier country"],
    "carrier_name": ["carrier", "haulier", "forwarder"],
    "carrier_type": ["carrier type", "mode"],
    PERIOD: ["month", "monthly", "trend", "over time"],
}
TIME_WORDS = [
    (r"\bq1\b", "q1"), (r"\bq2\b", "q2"), (r"\bq3\b", "q3"), (r"\bq4\b", "q4"),
    (r"(across|around|either side of|over) the (july )?tariff", "across_tariff_step"),
    (r"before the (july )?tariff|pre[- ]tariff", "pre_tariff_step"),
    (r"after the (july )?tariff|post[- ]tariff", "post_tariff_step"),
    (r"this quarter|last quarter", "last_quarter"), (r"last month|this month|year end|year-end", "last_month"),
]
POINT_IN_TIME = {"days_of_inventory", "doi_units", "inventory_turns"}
VALUE_ALIASES = {
    "tuas": ("plant_id", "PLT-SG01"), "joliet": ("plant_id", "PLT-US01"), "esslingen": ("plant_id", "PLT-DE01"),
    "mcdonough": ("plant_id", "DC-US01"), "venlo": ("plant_id", "DC-NL01"),
    "air carriers": ("carrier_type", "AIR"), "ocean": ("carrier_type", "OCEAN"),
}


@dataclass
class Resolution:
    query: dict[str, Any] | None
    refusal: str | None = None
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {"query": self.query, "refusal": self.refusal, "notes": self.notes}


def _phrases(registry: Registry, persona: str | None) -> list[tuple[str, str]]:
    found = []
    for name, metric in registry.metrics.items():
        words = {name.replace("_", " "), metric["title"].lower(), *map(str.lower, metric["synonyms"])}
        for role, phrases in metric["persona_synonyms"].items():
            if persona in (None, role):
                words.update(map(str.lower, phrases))
        found.extend((w.lower(), name) for w in words if w)
    return sorted(found, key=lambda p: -len(p[0]))


def resolve(registry: Registry, question: str, persona: str | None = None,
            dimension_values: dict[str, list[str]] | None = None) -> Resolution:
    text = " " + re.sub(r"\s+", " ", question.lower()) + " "
    if INJECTION.search(text):
        return Resolution(None, "prompt_injection")
    if RAW_ACCESS.search(text):
        return Resolution(None, "raw_sql" if re.search(r"select|delete|drop|insert|update|truncate", text) else "table_access")

    metrics, consumed = [], text
    for phrase, name in _phrases(registry, persona):
        pattern = r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])"
        if re.search(pattern, consumed) and name not in metrics:
            metrics.append(name)
            consumed = re.sub(pattern, " ", consumed)
    if not metrics:
        return Resolution(None, "out_of_ontology")
    notes = []
    for m in metrics:
        if registry.metrics[m]["parent"] is None and registry.metrics[m]["variants"]:
            notes.append(f"{m} resolved to the governed default; variants: {', '.join(registry.metrics[m]['variants'])}")

    values = dimension_values or {}
    filters, dims = [], []
    for alias, (dim, value) in VALUE_ALIASES.items():
        if alias in consumed:
            filters.append({"dimension": dim, "operator": "=", "value": value})
            consumed = consumed.replace(alias, " ")
    for dim, known in values.items():
        for value in sorted(known, key=len, reverse=True):
            # Short codes such as IN or US would match ordinary words; they must appear as written.
            if value.isupper() and len(value) <= 3:
                hit = re.search(r"(?<![A-Za-z])" + re.escape(value) + r"(?![A-Za-z])", question)
            else:
                hit = re.search(r"(?<![a-z])" + re.escape(value.lower()) + r"(?![a-z])", consumed)
            if hit:
                if not any(f["dimension"] == dim for f in filters):
                    filters.append({"dimension": dim, "operator": "=", "value": value})
                consumed = consumed.replace(value.lower(), " ")

    phrases = sorted(((w, d) for d, ws in DIMENSION_WORDS.items() for w in ws), key=lambda p: -len(p[0]))
    for w, dim in phrases:
        grouped_by = re.search(r"\b(by|per|across|each|which)\s+(\w+\s)?" + re.escape(w) + r"\b", consumed)
        if grouped_by or (dim == PERIOD and re.search(r"\b" + w + r"\b", consumed)):
            if dim not in dims and not any(f["dimension"] == dim for f in filters):
                dims.append(dim)
            consumed = consumed.replace(w, " ")
    if ("worst" in text or "best" in text) and "supplier" in text and "supplier_name" not in dims:
        dims.append("supplier_name")

    time_range = "last_month" if set(metrics) <= POINT_IN_TIME else "fy2026"
    for pattern, label in TIME_WORDS:
        if re.search(pattern, text):
            time_range = label
            break
    if PERIOD in dims and time_range == "last_month":
        time_range = "fy2026"
    return Resolution({"metrics": metrics, "dimensions": dims, "time": {"range": time_range},
                       "filters": filters}, notes=notes)
