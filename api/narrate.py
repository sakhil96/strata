"""The sentence that leads an answer, written from the persona's own result rather than by the model,
and the agent's account of how it read the question, cleaned to plain words."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
RANKING = re.compile(r"\b(worst|best|lowest|highest|top|bottom|most|least|rank|ranking|which)\b", re.I)
MARKDOWN = [
    (re.compile(r"```.*?```", re.S), " "),
    (re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", re.M), " "),
    (re.compile(r"^\s*\|.*\|\s*$", re.M), " "),
    (re.compile(r"^\s{0,3}#{1,6}\s*", re.M), ""),
    (re.compile(r"^\s*[-*+]\s+", re.M), ""),
    (re.compile(r"(?<!\w)_{1,2}([^_\n]+)_{1,2}(?!\w)"), r"\1"),
    (re.compile(r"[*`|>~]"), ""),
]
# Amounts, rates and decimals; a year or a day of the month is part of a window, not an amount.
AMOUNT = re.compile(r"\d[\d,]*\.\d|\d\s*(%|percent|points)|[$€£]\s*\d|\b\d{1,3}(,\d{3})+\b|\b(?!(19|20)\d{2}\b)\d{3,}\b", re.I)
HASH = re.compile(r"\b[0-9a-f]{12,}\b")


def month(iso: Any) -> str:
    d = iso if isinstance(iso, date) else date.fromisoformat(str(iso)[:10])
    return f"{MONTHS[d.month - 1]} {d.year}"


def value(v: float | None, unit: str) -> str:
    if v is None:
        return "no value"
    if unit == "ratio":
        return f"{v * 100:.1f}%"
    if unit == "usd_per_unit":
        return f"${v:,.2f}"
    if unit == "days":
        return f"{v:,.1f} days"
    if unit == "hours":
        return f"{v:,.1f} hours"
    if unit == "turns_per_year":
        return f"{v:,.1f} turns a year"
    return f"{v:,.2f}"


def change(first: float, last: float, unit: str) -> str:
    delta = last - first
    size = f"{abs(delta) * 100:.1f} points" if unit == "ratio" else value(abs(delta), unit)
    pct = f", {abs(delta) / abs(first) * 100:.1f}%" if first else ""
    return f"{size}{pct}"


def plain(text: str | None) -> str:
    out = text or ""
    for pattern, repl in MARKDOWN:
        out = pattern.sub(repl, out)
    return re.sub(r"\s+", " ", out).strip()


def reading(narrative: str | None) -> str | None:
    """At most two sentences on how the question was read; nothing that carries an amount, a rate or a hash."""
    text = plain(narrative)
    if not text:
        return None
    sentences = re.split(r"(?<=[.!?])\s+", text)[:2]
    kept = " ".join(sentences).strip()
    if AMOUNT.search(kept) or HASH.search(kept) or "SELECT" in kept.upper().split():
        return None
    return kept[:400] or None


def _title(card: dict[str, Any]) -> str:
    return card["title"][:1].upper() + card["title"][1:]


def lead(answer: dict[str, Any], question: str = "", dimension_titles: dict[str, str] | None = None) -> str | None:
    rows = answer.get("rows") or []
    query = answer["canonical_query"]
    metric = query["metrics"][0]
    card = next((m for m in answer["metrics"] if m["name"] == metric), answer["metrics"][0])
    unit = card["unit"]
    title = _title(card)
    dims = query.get("dimensions") or []
    points = [r for r in rows if r.get(metric) is not None]
    if not points:
        return f"{title} has no value for this window."
    period = f"{month(query['time']['start'])} to {month(query['time']['end'])}"
    if query["time"]["start"] == query["time"]["end"]:
        period = month(query["time"]["start"])

    if not dims:
        return f"{title} was {value(float(points[0][metric]), unit)} for {period}."

    if dims == ["period_month"]:
        series = sorted(points, key=lambda r: str(r["period_month"]))
        first, last = series[0], series[-1]
        v0, v1 = float(first[metric]), float(last[metric])
        if len(series) == 1:
            return f"{title} was {value(v0, unit)} in {month(first['period_month'])}."
        verb = "rose" if v1 > v0 else "fell" if v1 < v0 else "held"
        text = (f"{title} {verb} from {value(v0, unit)} in {month(first['period_month'])} to "
                f"{value(v1, unit)} in {month(last['period_month'])}")
        text += f", {'up' if v1 > v0 else 'down'} {change(v0, v1, unit)}." if v1 != v0 else "."
        values = [float(r[metric]) for r in series]
        lo, hi = min(range(len(values)), key=values.__getitem__), max(range(len(values)), key=values.__getitem__)
        turns = any((values[i] - values[i - 1]) * (values[i + 1] - values[i]) < 0 for i in range(1, len(values) - 1))
        if turns:
            text += (f" The low was {value(values[lo], unit)} in {month(series[lo]['period_month'])} and the high "
                     f"{value(values[hi], unit)} in {month(series[hi]['period_month'])}.")
        return text

    dim = next(d for d in dims if d != "period_month")
    label = (dimension_titles or {}).get(dim, dim.replace("_", " ")).lower()
    ordered = sorted(points, key=lambda r: float(r[metric]))
    low, high = ordered[0], ordered[-1]
    if RANKING.search(question or ""):
        return (f"Of {len(points)} {label} values, {low[dim]} is lowest on {card['title'].lower()} at "
                f"{value(float(low[metric]), unit)} and {high[dim]} highest at {value(float(high[metric]), unit)}, "
                f"{period}.")
    return (f"{title} ranges from {value(float(low[metric]), unit)} for {low[dim]} to "
            f"{value(float(high[metric]), unit)} for {high[dim]} across {len(points)} {label} values, {period}.")
