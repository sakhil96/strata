"""Suite 4, the parts that can be proven from the repository. The account half
(DESCRIBE AGENT, SHOW GRANTS, policy behaviour per role, GET_LINEAGE, YAML round trip)
lives in eval/account/ and runs only with SCM_BACKEND=snowflake."""

from __future__ import annotations

import json
import os
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
    assert "runs it again as the asker's persona" in orchestration


def test_explore_agent_is_the_only_analyst_and_only_engineers_can_use_it():
    sql = (ROOT / "snowflake" / "agent" / "create_explore_agent.sql").read_text()
    assert "cortex_analyst_text_to_sql" in sql
    grantees = set(re.findall(r"GRANT USAGE ON AGENT \S+SCM_EXPLORE_AGENT TO ROLE (\w+)", sql))
    assert grantees == {"SCM_DEPLOY"}


def test_instructions_file_and_agent_spec_say_the_same_things():
    text = INSTRUCTIONS.read_text().lower()
    orchestration = agent_spec()["instructions"]["orchestration"].lower()
    for rule in ("governed_query is the only source of a number", "runs it again as the asker's persona", "on_time_to_request", "supplier_on_time_receipt",
                 "carrier_on_time", "dio_financial", "line_fill_rate", "order_fill_rate"):
        assert rule in text and rule in orchestration, rule
    for refusal in ("run sql", "tables", "instructions"):
        assert refusal in text and refusal in orchestration


def test_every_metric_with_variants_names_its_default_to_the_agent(registry):
    text = INSTRUCTIONS.read_text().lower()
    orchestration = agent_spec()["instructions"]["orchestration"].lower()
    families = {name for name, m in registry.metrics.items() if m.get("variants")}
    assert families == {"on_time_delivery", "unit_fill_rate", "days_of_inventory"}
    for name in families:
        assert f"is {name}" in text and f"is {name}" in orchestration, name


def test_the_agent_reads_positions_at_the_last_month_as_the_registry_windows_say(registry):
    positions = sorted(n for n, m in registry.metrics.items() if m["window"] in ("point_in_time", "trailing_90_days"))
    assert positions == ["days_of_inventory", "doi_units", "inventory_turns"]
    orchestration = " ".join(agent_spec()["instructions"]["orchestration"].split())
    text = " ".join(INSTRUCTIONS.read_text().split())
    phrase = "days_of_inventory, doi_units and inventory_turns, which read last_month"
    assert phrase in orchestration and phrase in text


def test_the_query_tool_lists_every_governed_metric_and_dimension(registry):
    spec = agent_spec()
    tool = next(t["tool_spec"] for t in spec["tools"] if t["tool_spec"]["name"] == "GOVERNED_QUERY")
    described = tool["input_schema"]["properties"]["query"]["description"]
    for name in [*registry.metrics, *registry.dimensions]:
        assert re.search(rf"\b{name}\b", described), name


def test_no_physical_table_names_reach_the_agent():
    spec_text = yaml.safe_dump(agent_spec()["instructions"]) + INSTRUCTIONS.read_text()
    for forbidden in ("RAW.", "CONFORMED.", "STAGING.", "FCT_", "DIM_", "STG_"):
        assert forbidden not in spec_text.upper().replace("FCT_ ", ""), forbidden


def test_answer_contract_fields_are_shown_by_the_page_and_never_written_by_the_agent():
    text = INSTRUCTIONS.read_text().lower()
    for field in ("definition", "canonical query", "semantic_query_hash", "semantic_view() sql", "lineage", "role"):
        assert field in text, field
    response = " ".join(agent_spec()["instructions"]["response"].lower().split())
    assert "at most two plain sentences" in response
    for banned in ("numbers", "hashes", "sql", "markdown", "tables"):
        assert banned in response.split("no ", 1)[1], banned


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
    # Personas cannot select from SEMANTIC_BASE, and only supplier_unit_cost reaches a semantic view,
    # so most rules are reached only by the owner. This evaluates, under each role, the exact CASE the
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


def _metric_exprs(body):
    # The account reads names back in upper case; expressions come back as written.
    return {m["name"].lower(): m["expr"] for t in body["tables"] for m in t.get("metrics", [])}


def _exposures():
    return {(column, view): rule["expose"]["as"] for column, rule in ENTITLEMENTS["columns"].items()
            if "expose" in rule for view in rule["expose"]["in"]}


def test_only_the_procurement_and_logistics_views_expose_supplier_unit_cost():
    assert _exposures() == {("FCT_PO_LINE.UNIT_COST", "PROCUREMENT_SV"): "supplier_unit_cost",
                            ("FCT_PO_LINE.UNIT_COST", "LOGISTICS_SV"): "supplier_unit_cost"}
    for path in SEMANTIC_DIR.glob("*_v1.yaml"):
        body = yaml.safe_load(path.read_text())
        exposed = {d["name"] for t in body["tables"] for d in t.get("dimensions", []) if d["expr"] == "UNIT_COST"}
        expected = {"supplier_unit_cost"} if path.stem in ("procurement_sv_v1", "logistics_sv_v1") else set()
        assert exposed == expected, path.name


def test_exposing_a_governed_column_leaves_every_metric_expression_as_the_governed_view_has_it():
    def metrics(name):
        return _metric_exprs(yaml.safe_load((SEMANTIC_DIR / f"{name}_v1.yaml").read_text()))

    governed = metrics("scm_governed")
    assert len(governed) == 19
    for view in ("planning_sv", "procurement_sv", "logistics_sv", "executive_sv"):
        assert metrics(view) == governed, view


@pytest.mark.parametrize("role, view, shown", [("PROCUREMENT_ROLE", "PROCUREMENT_SV_V1", True),
                                               ("LOGISTICS_ROLE", "LOGISTICS_SV_V1", False)])
def test_on_the_account_supplier_unit_cost_shows_or_nulls_as_the_registry_says(account, role, view, shown):
    cursor, db = account
    assert (role in ENTITLEMENTS["columns"]["FCT_PO_LINE.UNIT_COST"]["show"]) is shown
    _as(cursor, role)
    cursor.execute(f"SELECT COUNT(*), COUNT(supplier_unit_cost) FROM SEMANTIC_VIEW({db}.SEMANTIC.{view} "
                   "DIMENSIONS po_lines.po_line_id, po_lines.supplier_unit_cost)")
    lines, costed = cursor.fetchone()
    assert lines > 0
    assert costed == (lines if shown else 0), (role, lines, costed)


def test_on_the_account_the_deployed_views_round_trip_with_the_governed_expressions(account):
    cursor, db = account
    _as(cursor, "SCM_DEPLOY")
    for name in ("scm_governed", "procurement_sv", "logistics_sv"):
        cursor.execute("SELECT SYSTEM$READ_YAML_FROM_SEMANTIC_VIEW(%s)", (f"{db}.SEMANTIC.{name.upper()}_V1",))
        deployed = yaml.safe_load(cursor.fetchone()[0])
        committed = yaml.safe_load((SEMANTIC_DIR / f"{name}_v1.yaml").read_text())
        assert _metric_exprs(deployed) == _metric_exprs(committed) and len(_metric_exprs(deployed)) == 19, name
        dims = {d["name"].lower() for t in deployed["tables"] for d in t.get("dimensions", [])}
        assert ("supplier_unit_cost" in dims) is (name != "scm_governed"), name


def test_nothing_committed_names_an_environment_or_a_model_the_spec_does_not_run():
    snapshot = (ROOT / "eval" / "governance_snapshot.json").read_text()
    assert "agent" not in json.loads(snapshot)
    assert not re.search(r"SCM_(PROD|TEST|DEV)\b", snapshot)
    model = agent_spec()["models"]["orchestration"]
    for name in ("governance", "operations", "eval-report"):
        recorded = (ROOT / "web" / "public" / "recorded" / f"{name}.json").read_text()
        assert not re.search(r"SCM_PROD\b", recorded), name
        assert set(re.findall(r"claude-[\w.-]+", recorded)) <= {model}, name


SERVICE_PERSONAS = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE", "EMEA_PLANNING_ROLE"]


def test_the_service_assumes_personas_through_its_own_role_never_through_its_default_role():
    roles = (ROOT / "snowflake" / "setup" / "01_roles.sql").read_text()
    for persona in SERVICE_PERSONAS:
        assert f"GRANT ROLE {persona} TO ROLE SCM_SERVICE_PERSONAS;" in roles, persona
        assert f"GRANT ROLE {persona} TO ROLE SCM_SERVICE_ROLE;" not in roles, persona
    assert "GRANT ROLE SCM_SERVICE_PERSONAS TO USER SCM_SERVICE_USER;" in roles
    assert "GRANT ROLE SCM_SERVICE_PERSONAS TO ROLE" not in roles
    assert "DEFAULT_SECONDARY_ROLES = ()" in roles


@pytest.mark.skipif(not os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"), reason="needs account: the service user's key")
def test_on_the_account_the_service_user_assumes_exactly_the_personas(account):
    import snowflake.connector
    from cryptography.hazmat.primitives import serialization

    _, db = account
    key = serialization.load_pem_private_key(Path(os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]).read_bytes(), password=None)
    with snowflake.connector.connect(account=os.environ["SNOWFLAKE_ACCOUNT"], host=os.environ["SNOWFLAKE_HOST"],
                                     user=os.getenv("SNOWFLAKE_USER", "SCM_SERVICE_USER"), private_key=key,
                                     database=db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT CURRENT_ROLE(), " + ", ".join(f"IS_ROLE_IN_SESSION('{r}')" for r in SERVICE_PERSONAS))
        default, *in_session = cur.fetchone()
        assert default == "SCM_SERVICE_ROLE" and not any(in_session)
        for persona in SERVICE_PERSONAS:
            _as(cur, persona)
            cur.execute("SELECT CURRENT_ROLE()")
            assert cur.fetchone()[0] == persona
        for other in ("SCM_DEPLOY", "SCM_ADMIN", "JUDGE_ROLE"):
            with pytest.raises(snowflake.connector.errors.ProgrammingError):
                _as(cur, other)


@pytest.mark.skipif(os.getenv("SCM_AGENT") != "on", reason="needs account: agent:run with the service key")
def test_on_the_account_a_scoped_persona_gets_the_same_scoped_answer_on_ask_and_in_the_builder(account):
    from fastapi.testclient import TestClient

    from api.main import app

    cursor, db = account
    _as(cursor, "SCM_DEPLOY")
    cursor.execute(f"SELECT plant_id FROM {db}.CONFORMED.DIM_PLANT WHERE region = 'EMEA'")
    emea = {r[0] for r in cursor.fetchall()}
    client = TestClient(app)
    question = "What is on-time delivery by plant for FY2026?"
    asked = client.post("/api/ask", json={"question": question}, headers={"X-Persona": "EMEA_PLANNING_ROLE"}).json()
    assert asked["path"] == "agent" and asked["role"] == "EMEA_PLANNING_ROLE" and asked["view"] == "PLANNING_SV_V1"
    built = client.post("/api/query", json={"query": asked["canonical_query"]},
                        headers={"X-Persona": "EMEA_PLANNING_ROLE"}).json()
    assert built["semantic_query_hash"] == asked["semantic_query_hash"]
    assert built["rows"] == asked["rows"] and asked["rows"]
    for answer in asked["answers"]:
        assert answer["role"] == "EMEA_PLANNING_ROLE"
        if "plant_id" in answer["canonical_query"]["dimensions"]:
            assert {r["plant_id"] for r in answer["rows"]} <= emea
    planner = client.post("/api/query", json={"query": asked["canonical_query"]},
                          headers={"X-Persona": "PLANNING_ROLE"}).json()
    assert planner["semantic_query_hash"] == asked["semantic_query_hash"]
    assert {r["plant_id"] for r in planner["rows"]} > emea
