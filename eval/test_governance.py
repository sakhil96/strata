"""Suite 4, the parts that can be proven from the repository. The account half
(DESCRIBE AGENT, SHOW GRANTS, policy behaviour per role, GET_LINEAGE, YAML round trip)
lives in eval/account/ and runs only with SCM_BACKEND=snowflake."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

import semantic

ROOT = Path(__file__).resolve().parent.parent
AGENT_SQL = ROOT / "snowflake" / "agent" / "create_agent.sql"
INSTRUCTIONS = ROOT / "snowflake" / "agent" / "instructions.md"
SEMANTIC_DIR = ROOT / "snowflake" / "semantic"
GOVERNED_TOOLS = {"GOVERNED_QUERY", "DESCRIBE_METRIC", "EXPLAIN_LINEAGE"}


def agent_spec() -> dict:
    body = re.search(r"FROM SPECIFICATION\s*\$\$(.*?)\$\$", AGENT_SQL.read_text(), re.S).group(1)
    return yaml.safe_load(body.replace("{{DB}}", "SCM_DEV").replace("{{WH}}", "SCM_WH_DEV"))


def test_agent_has_no_tool_that_runs_sql_it_writes():
    tools = {t["tool_spec"]["name"]: t["tool_spec"]["type"] for t in agent_spec()["tools"]}
    generic = {n for n, kind in tools.items() if kind == "generic"}
    assert generic == GOVERNED_TOOLS
    assert set(tools.values()) <= {"generic", "cortex_search"}
    assert "sql_exec" not in " ".join(tools).lower()


def test_every_generic_tool_is_one_of_our_procedures():
    resources = agent_spec()["tool_resources"]
    for name in GOVERNED_TOOLS:
        assert resources[name]["type"] == "procedure"
        assert resources[name]["identifier"].endswith(f".AGENT.{name}")


def test_orchestration_model_is_pinned_not_auto():
    assert agent_spec()["models"]["orchestration"] not in ("auto", None, "")


def test_answer_agent_has_no_analyst_tool_and_reports_the_hash():
    # The tool set is the enforcement: on the account the model answered from Analyst's own SQL
    # despite being told not to, so the answer agent carries no tool that can produce a number
    # except GOVERNED_QUERY.
    spec = agent_spec()
    assert all(t["tool_spec"]["type"] != "cortex_analyst_text_to_sql" for t in spec["tools"])
    orchestration = spec["instructions"]["orchestration"].lower()
    assert "governed_query is the only source of a number" in orchestration
    assert "semantic_query_hash beside it" in orchestration


def test_explore_agent_is_the_only_analyst_and_only_engineers_can_use_it():
    sql = (ROOT / "snowflake" / "agent" / "create_explore_agent.sql").read_text()
    assert "cortex_analyst_text_to_sql" in sql
    grantees = set(re.findall(r"GRANT USAGE ON AGENT \S+SCM_EXPLORE_AGENT TO ROLE (\w+)", sql))
    assert grantees == {"SCM_DEPLOY"}


def test_instructions_file_and_agent_spec_say_the_same_things():
    text = INSTRUCTIONS.read_text().lower()
    orchestration = agent_spec()["instructions"]["orchestration"].lower()
    for rule in ("governed_query is the only source of a number", "semantic_query_hash beside it", "on_time_to_request", "supplier_on_time_receipt",
                 "carrier_on_time", "dio_financial", "line_fill_rate", "order_fill_rate"):
        assert rule in text and rule in orchestration, rule
    for refusal in ("run sql", "tables", "instructions"):
        assert refusal in text and refusal in orchestration


def test_no_physical_table_names_reach_the_agent():
    spec_text = yaml.safe_dump(agent_spec()["instructions"]) + INSTRUCTIONS.read_text()
    for forbidden in ("RAW.", "CONFORMED.", "STAGING.", "FCT_", "DIM_", "STG_"):
        assert forbidden not in spec_text.upper().replace("FCT_ ", ""), forbidden


def test_answer_contract_fields_are_required_by_the_instructions():
    text = INSTRUCTIONS.read_text().lower()
    for field in ("definition", "canonical query", "semantic_query_hash", "semantic_view() sql", "lineage", "role"):
        assert field in text, field


@pytest.mark.parametrize("view", ["scm_governed", "planning_sv", "procurement_sv", "logistics_sv", "executive_sv"])
def test_every_view_ships_a_verified_query_for_every_governed_question(view):
    body = yaml.safe_load((SEMANTIC_DIR / f"{view}_v1.yaml").read_text())
    questions = [q for q in yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text())["questions"]
                 if q["scope"] == "in_scope"]
    names = {v["name"] for v in body["verified_queries"]}
    assert names == {q["id"] for q in questions}
    for v in body["verified_queries"]:
        assert v["sql"].startswith(f"SELECT * FROM SEMANTIC_VIEW(\n    {view.upper()}_V1")


def test_verified_query_sql_is_exactly_what_governed_query_would_run(registry):
    body = yaml.safe_load((SEMANTIC_DIR / "planning_sv_v1.yaml").read_text())
    by_id = {q["id"]: q for q in yaml.safe_load((ROOT / "eval" / "questions.yaml").read_text())["questions"]}
    for v in body["verified_queries"]:
        canonical = semantic.canonicalise(registry, by_id[v["name"]]["query"])
        assert v["sql"] == semantic.render_semantic_sql(registry, canonical, "PLANNING_SV_V1")


def test_prod_compile_refuses_a_metric_that_is_not_approved(tmp_path, monkeypatch):
    import compile as compiler

    registry = yaml.safe_load((ROOT / "ontology" / "metrics.yaml").read_text())
    registry["metrics"]["otif"]["status"] = "draft"
    draft = tmp_path / "metrics.yaml"
    draft.write_text(yaml.safe_dump(registry))
    problems = compiler.check_registry(semantic.load_registry(draft), "prod")
    assert any("otif" in p and "SCM_PROD" in p for p in problems)
    assert not compiler.check_registry(semantic.load_registry(draft), "dev")


def test_compile_refuses_a_metric_missing_a_required_field(tmp_path):
    registry = yaml.safe_load((ROOT / "ontology" / "metrics.yaml").read_text())
    del registry["metrics"]["unit_fill_rate"]["steward"]
    broken = tmp_path / "metrics.yaml"
    broken.write_text(yaml.safe_dump(registry))
    with pytest.raises(semantic.SemanticError, match="steward"):
        semantic.load_registry(broken)


POLICIES = ROOT / "snowflake" / "policies"
ENTITLEMENTS = yaml.safe_load((ROOT / "ontology" / "entitlements.yaml").read_text())


def test_every_governed_column_is_tagged_and_ruled_in_both_editions():
    tags = (POLICIES / "tags.sql").read_text()
    views = (POLICIES / "standard" / "secure_views.sql").read_text()
    enterprise = (POLICIES / "enterprise" / "policies.sql").read_text()
    for column in ("DIM_SUPPLIER.BANK_ACCOUNT", "DIM_SUPPLIER.CONTACT_EMAIL", "FCT_PO_LINE.UNIT_COST", "FCT_SHIPMENT.FREIGHT_CHARGE"):
        table, col = column.split(".")
        assert re.search(rf"CONFORMED.{table} MODIFY COLUMN {col} SET TAG .*SENSITIVITY", tags), column
        assert re.search(rf"END AS {col}\b", views), column
        assert f"MASK_{table}_{col}" in enterprise, column


def test_semantic_views_read_only_secure_views():
    views = (POLICIES / "standard" / "secure_views.sql").read_text()
    created = set(re.findall(r"CREATE OR REPLACE (SECURE )?VIEW \S+\.SEMANTIC_BASE\.(\w+)", views))
    assert all(secure for secure, _ in created)
    for path in SEMANTIC_DIR.glob("*_v1.yaml"):
        for table in yaml.safe_load(path.read_text())["tables"]:
            assert table["base_table"]["schema"] == "SEMANTIC_BASE", (path.name, table["name"])
            assert ("SECURE ", table["base_table"]["table"]) in created


def test_every_plant_scoped_table_is_filtered_by_the_entitlement_registry():
    views = (POLICIES / "standard" / "secure_views.sql").read_text()
    for table in ENTITLEMENTS["scoped_by_plant"]:
        body = views.split(f"SEMANTIC_BASE.{table}\n", 1)[1].split(";", 1)[0]
        assert "GOV.ENTITLEMENTS e WHERE IS_ROLE_IN_SESSION(e.role_name)" in body, table


def test_personas_share_one_scope_and_no_inherited_role_carries_one():
    roles = ENTITLEMENTS["roles"]
    assert {roles[r]["scope"] == "*" for r in ("PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE")} == {True}
    assert "SCM_READER" not in roles


def test_procedures_run_with_callers_rights_and_bind_their_parameters():
    ddl = (ROOT / "snowflake" / "procs" / "create_procs.sql").read_text()
    assert ddl.count("EXECUTE AS CALLER") == 4
    source = (ROOT / "snowflake" / "procs" / "governed_query.py").read_text()
    assert "params=[" in source
    assert "render_semantic_sql" in source and "canonicalise" in source


def test_setup_files_hold_no_passwords():
    for path in (ROOT / "snowflake").rglob("*.sql"):
        text = path.read_text()
        assert not re.search(r"PASSWORD\s*=\s*'(?!set-via-cli)[^']+'", text), path
        assert "MUST_CHANGE_PASSWORD" not in text, path


PERSONAS = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE", "EMEA_PLANNING_ROLE"]


def _as(cursor, role):
    cursor.execute("USE SECONDARY ROLES NONE")
    cursor.execute("USE ROLE IDENTIFIER(%s)", (role,))


@pytest.mark.parametrize("role", PERSONAS)
def test_on_the_account_each_role_sees_its_registry_scope_and_nothing_underneath(account, role):
    import snowflake.connector

    cursor, db = account
    scope = ENTITLEMENTS["roles"][role]["scope"]
    _as(cursor, "SCM_DEPLOY")
    cursor.execute(f"SELECT plant_id, region FROM {db}.CONFORMED.DIM_PLANT")
    plants = dict(cursor.fetchall())
    expected = sorted(plants) if scope == "*" else sorted(p for p, r in plants.items() if r in scope.get("region", [])
                                                         or p in scope.get("plant", []))
    view = {"EMEA_PLANNING_ROLE": "PLANNING_SV_V1"}.get(role, role.replace("_ROLE", "_SV_V1"))
    _as(cursor, role)
    cursor.execute(f"SELECT * FROM SEMANTIC_VIEW({db}.SEMANTIC.{view} DIMENSIONS plants.plant_id "
                   "METRICS delivered_lines.on_time_delivery) ORDER BY 1")
    assert [r[0] for r in cursor.fetchall()] == expected
    for forbidden in ("CONFORMED.FCT_SALES_ORDER_LINE", "RAW.SUPPLIER_MASTER", "SEMANTIC_BASE.DIM_SUPPLIER"):
        with pytest.raises(snowflake.connector.errors.ProgrammingError):
            cursor.execute(f"SELECT 1 FROM {db}.{forbidden} LIMIT 1")


ROLES_FOR_COLUMNS = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE", "EMEA_PLANNING_ROLE",
                     "SCM_SERVICE_ROLE"]


def test_on_the_account_every_column_rule_evaluates_as_the_registry_says_for_every_role(account):
    # Personas cannot select from SEMANTIC_BASE, and no semantic view carries a governed column, so
    # the rule is reached only by the owner. This evaluates, under each role, the exact CASE the
    # compiled secure view carries, with a literal standing in for the column, and compares the
    # outcome with GOV.COLUMN_VISIBILITY.
    cursor, db = account
    _as(cursor, "SCM_DEPLOY")
    cursor.execute("SHOW VIEWS IN SCHEMA IDENTIFIER(%s)", (f"{db}.SEMANTIC_BASE",))
    secure = {r[1]: r[8] for r in cursor.fetchall()}
    assert len(secure) == 10 and all(v == "true" for v in secure.values()), secure
    cursor.execute(f"SELECT table_name || '.' || column_name, role_name, rule FROM {db}.GOV.COLUMN_VISIBILITY")
    loaded = {(c, r): rule for c, r, rule in cursor.fetchall()}
    views = (POLICIES / "standard" / "secure_views.sql").read_text()
    for role in ROLES_FOR_COLUMNS:
        _as(cursor, role)
        for column in ENTITLEMENTS["columns"]:
            table, col = column.split(".")
            body = views.split(f"SEMANTIC_BASE.{table}\n", 1)[1].split(";", 1)[0]
            case = re.search(rf"(CASE WHEN (?:(?!\bEND\b).)*? END) AS {col}\b", body).group(1)
            case = case.replace(f"t.{col}", "'visible'")
            cursor.execute(f"SELECT {case}")
            seen = cursor.fetchone()[0]
            outcome = "show" if seen == "visible" else "masked" if seen == "***" else "null"
            assert outcome == loaded[(column, role)], (role, column, outcome)
