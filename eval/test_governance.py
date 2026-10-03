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


def test_sensitive_columns_are_tagged_and_masked_by_tag():
    policies = (SEMANTIC_DIR / "policies.sql").read_text()
    for column in ("bank_account", "contact_email", "unit_cost", "freight_charge"):
        assert re.search(rf"MODIFY COLUMN {column} SET TAG .*SENSITIVITY", policies), column
    setup = (ROOT / "snowflake" / "setup" / "04_policies.sql").read_text()
    assert "SYSTEM$GET_TAG_ON_CURRENT_COLUMN" in setup
    assert "ALTER TAG {{DB}}.CONFORMED.SENSITIVITY SET" in setup


def test_every_conformed_fact_with_a_plant_carries_the_row_access_policy():
    policies = (SEMANTIC_DIR / "policies.sql").read_text()
    for fact in ("FCT_SALES_ORDER_LINE", "FCT_SHIPMENT", "FCT_SHIPMENT_LINE", "FCT_PO_LINE", "FCT_INVENTORY_MONTH"):
        assert f"{fact} ADD ROW ACCESS POLICY" in policies


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
