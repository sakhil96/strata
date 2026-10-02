"""Suite 1: every governed metric and variant, at every grouping, equals the simulated truth."""

from __future__ import annotations

import math

import pandas as pd
import pytest
import yaml

import semantic

DIMS = ["plant_id", "region", "segment", "part_family"]
GROUPINGS = sorted({"month", "month,plant_id", "month,region", "month,segment", "month,part_family",
                    "month,plant_id,region,segment,part_family", "month,plant_id,region,part_family",
                    "month,plant_id,region,segment"})


def undefined(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def within_tolerance(expected: float, actual: float, metric_type: str) -> bool:
    if undefined(expected) or undefined(actual):
        return undefined(expected) and undefined(actual)
    if metric_type == "ratio" and abs(expected) <= 1.5:
        return abs(expected - actual) <= 0.0001
    return abs(expected - actual) <= max(0.005 * abs(expected), 1e-9)


def answer_by_grouping(warehouse, registry, metric: str, grouping: str) -> pd.DataFrame:
    dims = [d for d in grouping.split(",") if d != "month"]
    result = semantic.execute_local(warehouse, registry, {
        "metrics": [metric], "dimensions": ["period_month", *dims], "time": {"range": "fy2026"}})
    frame = pd.DataFrame(result["rows"])
    if frame.empty:
        return frame
    frame = frame.rename(columns={"period_month": "month"})
    frame["month"] = pd.to_datetime(frame["month"]).dt.date
    return frame


@pytest.mark.parametrize("grouping", GROUPINGS)
def test_every_metric_matches_truth_at_grouping(warehouse, registry, truth, grouping):
    for metric, rows in truth[truth.grouping == grouping].groupby("metric"):
        metric_type = registry.metrics[metric]["type"]
        keys = grouping.split(",")
        actual = answer_by_grouping(warehouse, registry, metric, grouping)
        expected = rows[[*keys, "value"]].copy()
        expected["month"] = pd.to_datetime(expected["month"]).dt.date
        for k in keys[1:]:
            expected[k] = expected[k].astype(str)
            actual[k] = actual[k].astype(str)
        merged = expected.merge(actual, on=keys, how="outer", indicator=True)
        missing = merged[merged._merge != "both"]
        assert missing.empty, f"{metric} at {grouping}: rows only on one side\n{missing.head()}"
        bad = merged[[not within_tolerance(e, a, metric_type) for e, a in zip(merged.value, merged[metric], strict=False)]]
        assert bad.empty, f"{metric} at {grouping} differs from truth\n{bad.head()}"
    if grouping == "month":
        assert truth[truth.grouping == "month"].metric.nunique() == len(registry.metrics)


def test_truth_covers_every_governed_metric_and_variant(registry, truth):
    assert set(truth.metric) == set(registry.metrics)


def test_ratios_are_ratios_of_sums_at_every_rollup(truth):
    ratios = truth[truth.numerator.notna()]
    for metric, rows in ratios.groupby("metric"):
        leaf_grouping = max(rows.grouping.unique(), key=lambda g: g.count(","))
        leaf = rows[rows.grouping == leaf_grouping]
        for grouping, coarse in rows.groupby("grouping"):
            keys = grouping.split(",")
            rolled = leaf.groupby(keys, dropna=False)[["numerator", "denominator"]].sum().reset_index()
            rolled = rolled[rolled.denominator != 0]
            joined = coarse.merge(rolled, on=keys, suffixes=("", "_leaf"))
            assert len(joined) == len(coarse), f"{metric} {grouping} lost rows when rolled up"
            assert (joined.numerator - joined.numerator_leaf).abs().max() < 1e-6
            assert (joined.denominator - joined.denominator_leaf).abs().max() < 1e-6


def test_average_of_plant_ratios_is_not_what_we_report(truth):
    month = truth[(truth.metric == "on_time_delivery") & (truth.grouping == "month")].iloc[0]
    plants = truth[(truth.metric == "on_time_delivery") & (truth.grouping == "month,plant_id")
                   & (truth.month == month.month)]
    assert abs(plants.value.mean() - month.value) > 1e-6
    assert abs(plants.numerator.sum() / plants.denominator.sum() - month.value) < 1e-12


def test_four_persona_views_carry_identical_metric_expressions():
    from compile import SEMANTIC_DIR

    def expressions(view: str) -> dict[str, str]:
        body = yaml.safe_load((SEMANTIC_DIR / f"{view}_v1.yaml").read_text())
        return {m["name"]: m["expr"] for t in body["tables"] for m in t.get("metrics", [])}

    governed = expressions("scm_governed")
    for view in ("planning_sv", "procurement_sv", "logistics_sv", "executive_sv"):
        assert expressions(view) == governed, view


def test_persona_views_return_identical_on_time_delivery_for_identical_filters(warehouse, registry):
    query = {"metrics": ["on_time_delivery"], "dimensions": ["region"], "time": {"range": "q3"},
             "filters": [{"dimension": "segment", "operator": "=", "value": "Industrial"}]}
    hashes = {semantic.execute_local(warehouse, registry, query)["semantic_query_hash"] for _ in range(4)}
    answers = [semantic.execute_local(warehouse, registry, query)["rows"] for _ in range(4)]
    assert len(hashes) == 1 and all(a == answers[0] for a in answers)


@pytest.mark.parametrize("lower,higher", [
    ("on_time_to_request", "on_time_delivery"),
    ("on_time_delivery", "carrier_on_time"),
    ("otif", "on_time_delivery"),
    ("order_fill_rate", "line_fill_rate"),
    ("line_fill_rate", "unit_fill_rate"),
])
def test_variants_differ_in_the_injected_direction(truth, lower, higher):
    fy = truth[truth.grouping == "month"].groupby("metric")[["numerator", "denominator"]].sum()
    rate = fy.numerator / fy.denominator
    assert rate[lower] < rate[higher]


def test_inventory_turns_times_days_of_inventory_is_365_in_every_grouping(truth):
    doi = truth[truth.metric == "days_of_inventory"].set_index(["grouping", "month", *DIMS]).value
    turns = truth[truth.metric == "inventory_turns"].set_index(["grouping", "month", *DIMS]).value
    product = (doi * turns).dropna()
    assert len(product) == len(doi)
    assert (product - 365).abs().max() < 1e-6


def test_landed_cost_steps_up_after_the_tariff_change(warehouse, registry):
    def landed(window: str) -> float:
        rows = semantic.execute_local(warehouse, registry, {
            "metrics": ["landed_cost_per_unit"], "time": {"range": window},
            "filters": [{"dimension": "part_family", "operator": "=", "value": "Control electronics"}]})["rows"]
        return rows[0]["landed_cost_per_unit"]

    assert landed("post_tariff_step") > landed("pre_tariff_step")
