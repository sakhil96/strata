"""Suite 3: one question, three roles, three phrasings: one hash and one number, 20 of 20."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import resolver
import scoring
import semantic

CASES = yaml.safe_load((Path(__file__).parent / "consistency_cases.yaml").read_text())["cases"]


def test_there_are_twenty_cases_each_asked_three_ways():
    assert len(CASES) == 20
    assert all(set(c["phrasings"]) == {"PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE"} for c in CASES)


def test_each_role_uses_only_its_own_vocabulary(registry):
    for case in CASES:
        metric = registry.metrics[case["query"]["metrics"][0]]
        for role, question in case["phrasings"].items():
            own = [p.lower() for p in metric["persona_synonyms"][role]]
            assert any(p in question.lower() for p in own), f"{case['id']} {role}: {question!r}"


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_three_roles_get_one_hash_and_one_number(case, registry, warehouse):
    values = scoring.dimension_values(warehouse)
    expected = semantic.canonicalise(registry, case["query"])
    answers = {}
    for role, question in case["phrasings"].items():
        resolution = resolver.resolve(registry, question, role, values)
        assert resolution.query, f"{role} could not place {question!r}"
        answers[role] = semantic.execute_local(warehouse, registry, resolution.query)
    hashes = {a["semantic_query_hash"] for a in answers.values()}
    assert hashes == {semantic.query_hash(expected)}
    assert len({repr(a["rows"]) for a in answers.values()}) == 1
