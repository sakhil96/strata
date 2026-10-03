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


ROLE_VIEW = {"PLANNING_ROLE": "PLANNING_SV_V1", "PROCUREMENT_ROLE": "PROCUREMENT_SV_V1", "LOGISTICS_ROLE": "LOGISTICS_SV_V1"}
REPORT_DIR = Path(__file__).parent / "report"


def _governed(cursor, db: str, role: str, query: dict, question: str) -> dict:
    import json

    cursor.execute("USE SECONDARY ROLES NONE")
    cursor.execute("USE ROLE IDENTIFIER(%s)", (role,))
    cursor.execute(f"CALL {db}.AGENT.GOVERNED_QUERY(%s, %s, %s)", (ROLE_VIEW[role], json.dumps(query), question))
    value = cursor.fetchone()[0]
    return json.loads(value) if isinstance(value, str) else value


def test_on_the_account_three_roles_get_one_hash_and_one_number_for_every_case(account, registry):
    import json

    cursor, db = account
    table, failures = [], []
    for case in CASES:
        local = semantic.query_hash(semantic.canonicalise(registry, case["query"]))
        answers = {role: _governed(cursor, db, role, case["query"], question)
                   for role, question in case["phrasings"].items()}
        hashes = {a.get("semantic_query_hash") for a in answers.values()}
        rows = {json.dumps(a.get("rows"), sort_keys=True) for a in answers.values()}
        ok = hashes == {local} and len(rows) == 1
        failures += [] if ok else [case["id"]]
        first = next(iter(answers.values()))
        table.append({"case": case["id"], "metric": case["query"]["metrics"][0],
                      "dimensions": case["query"]["dimensions"], "hash": local, "rows": first.get("row_count"),
                      "value": (first.get("rows") or [{}])[0], "identical": ok})
    REPORT_DIR.mkdir(exist_ok=True)
    (REPORT_DIR / "persona_account.json").write_text(json.dumps(table, indent=2, default=str) + "\n")
    lines = [f"# Persona consistency on {db}", "",
             "Each case run through GOVERNED_QUERY as PLANNING_ROLE, PROCUREMENT_ROLE and LOGISTICS_ROLE, "
             "each against its own semantic view. `identical` means all three returned the same rows and a "
             "semantic_query_hash equal to the local engine's.", "",
             "| case | metric | breakdown | rows | semantic_query_hash | identical |", "|---|---|---|---|---|---|"]
    lines += [f"| {t['case']} | {t['metric']} | {', '.join(t['dimensions']) or '-'} | {t['rows']} | "
              f"`{t['hash'][:16]}` | {'yes' if t['identical'] else 'NO'} |" for t in table]
    (REPORT_DIR / "persona_account.md").write_text("\n".join(lines) + "\n")
    assert not failures, failures


AGENT_QUESTIONS = ["What is on-time delivery for FY2026?", "Which suppliers have the worst on-time receipt?",
                   "How did landed cost move by month across the July tariff step?", "What is DOI by plant?"]


def test_every_numeric_agent_answer_has_an_audit_row_with_its_hash(account):
    import os

    import agent_audit

    if not os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"):
        pytest.skip("needs account: the service user's key (SNOWFLAKE_PRIVATE_KEY_PATH) signs agent:run")
    cursor, db = account
    replies = [agent_audit.ask(os.environ["SNOWFLAKE_HOST"], db, q) for q in AGENT_QUESTIONS]
    rows = agent_audit.reconcile(replies, cursor, db, os.environ["SNOWFLAKE_USER"])
    numeric = [r for r in rows if r["numeric"]]
    assert numeric, "no numeric answers to reconcile"
    assert sum(r["reconciled"] for r in numeric) == len(numeric), [r["question"] for r in numeric if not r["reconciled"]]
