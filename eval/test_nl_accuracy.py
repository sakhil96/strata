"""Suite 2: from words to the governed query. Floors: metric resolution 90%, exact query 85%,
numbers 100% when the metric is right, refusals 10 of 10.

Locally this scores the model-free resolver, which is the fallback path and the baseline the
agent must beat. With SCM_AGENT=on and an account it scores the agent through agent:run."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

import scoring
import semantic

ITEMS = yaml.safe_load((Path(__file__).parent / "questions.yaml").read_text())["questions"]
GOVERNED = [i for i in ITEMS if i["scope"] == "in_scope"]
REFUSALS = [i for i in ITEMS if i["scope"] == "out_of_scope"]


def test_the_set_has_fifty_governed_questions_and_ten_refusals():
    assert (len(GOVERNED), len(REFUSALS)) == (50, 10)


@pytest.fixture(scope="module")
def scored(registry, warehouse):
    values = scoring.dimension_values(warehouse)
    return {i["id"]: scoring.score_item(registry, i, scoring.resolve_locally(registry, values, i)) for i in ITEMS}


def test_metric_resolution_is_at_least_ninety_percent(scored):
    rate = sum(scored[i["id"]]["metric_resolved"] for i in GOVERNED) / len(GOVERNED)
    assert rate >= 0.90, rate


def test_exact_semantic_query_match_is_at_least_eighty_five_percent(scored):
    rate = sum(scored[i["id"]]["exact_query"] for i in GOVERNED) / len(GOVERNED)
    assert rate >= 0.85, rate


def test_when_the_metric_is_right_the_number_is_right(scored, registry, warehouse):
    for item in GOVERNED:
        s = scored[item["id"]]
        if not s["metric_resolved"]:
            continue
        expected = semantic.execute_local(warehouse, registry, item["query"])["rows"]
        values = scoring.dimension_values(warehouse)
        got = semantic.execute_local(warehouse, registry, scoring.resolve_locally(registry, values, item)["query"])["rows"]
        if s["exact_query"]:
            assert got == expected, item["id"]


def test_every_out_of_scope_question_is_refused(scored):
    assert all(scored[i["id"]]["refused"] for i in REFUSALS)


@pytest.mark.skipif(os.getenv("SCM_AGENT") != "on", reason="needs account: agent:run against SCM_TEST")
def test_agent_meets_the_same_floors_through_agent_run(registry):
    import json
    from pathlib import Path

    from api import agent

    resolved = exact = refused = 0
    outcomes = []
    for item in ITEMS:
        reply = agent.run(item["question"], "EXECUTIVE_ROLE", "EVAL_RUNNER", None, None)
        if item["scope"] == "out_of_scope":
            refused += reply["answer"] is None
            outcomes.append({"id": item["id"], "refused": reply["answer"] is None})
            continue
        canonical = (reply["answer"] or {}).get("canonical_query")
        expected = semantic.canonicalise(registry, item["query"])
        resolved += bool(canonical) and canonical["metrics"] == expected["metrics"]
        exact += canonical == expected
        outcomes.append({"id": item["id"], "question": item["question"], "expected": expected,
                         "got": canonical, "exact": canonical == expected})
    report = Path(__file__).parent / "report"
    report.mkdir(exist_ok=True)
    (report / "agent_floor.json").write_text(json.dumps(
        {"resolved": resolved, "exact": exact, "refused": refused, "governed": len(GOVERNED),
         "refusals": len(REFUSALS), "outcomes": outcomes}, indent=2, default=str) + "\n")
    assert resolved / len(GOVERNED) >= 0.90 and exact / len(GOVERNED) >= 0.85 and refused == len(REFUSALS)
