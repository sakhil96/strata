import json
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _stub_snowflake_runtime() -> None:
    # The procedures run inside Snowflake, which provides snowpark and telemetry; CI does not install
    # either, and the code under test only needs the Session name and two telemetry calls.
    if "snowflake.snowpark" in sys.modules:
        return
    try:
        import snowflake.snowpark
        import snowflake.telemetry  # noqa: F401
        return
    except ImportError:
        pass
    try:
        import snowflake as package
    except ImportError:
        package = sys.modules.setdefault("snowflake", types.ModuleType("snowflake"))
        package.__path__ = []
    snowpark = types.ModuleType("snowflake.snowpark")
    snowpark.Session = object
    telemetry = types.ModuleType("snowflake.telemetry")
    telemetry.set_span_attribute = lambda key, value: None
    package.snowpark, package.telemetry = snowpark, telemetry
    sys.modules["snowflake.snowpark"], sys.modules["snowflake.telemetry"] = snowpark, telemetry


_stub_snowflake_runtime()
sys.path[:0] = [str(ROOT / "snowflake" / "procs"), str(ROOT / "ontology")]

import describe_metric  # noqa: E402
import explain_lineage  # noqa: E402
import governed_query  # noqa: E402


class Row(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)

    def as_dict(self):
        return dict(self)


class Ledger:
    # A session that answers the statements the procedures send and keeps every one it saw.

    def __init__(self, database="SCM_DEV", role="LOGISTICS_ROLE", answer=None, lineage=None, glossary=None,
                 metrics=("on_time_delivery", "otif"), dimensions=("region", "carrier_name"), fail_query=False):
        self.database, self.role, self.query_tag = database, role, ""
        self.answer = answer if answer is not None else [Row(ON_TIME_DELIVERY=0.837553)]
        self.lineage, self.glossary = lineage, glossary or {}
        self.metrics, self.dimensions, self.fail_query = metrics, dimensions, fail_query
        self.statements: list[tuple[str, list | None]] = []

    def get_current_database(self):
        return f'"{self.database}"' if self.database else None

    def get_current_role(self):
        return f'"{self.role}"'

    def sql(self, text, params=None):
        self.statements.append((text, params))
        return types.SimpleNamespace(collect=lambda: self._answer(text, params))

    def _answer(self, text, params):
        if text.startswith("SHOW SEMANTIC METRICS"):
            return [Row(name=m.upper()) for m in self.metrics]
        if text.startswith("SHOW SEMANTIC DIMENSIONS"):
            return [Row(name=d.upper()) for d in self.dimensions]
        if text.startswith("SELECT CURRENT_USER()"):
            return [Row(USER="STRATA_CHECK_LOGISTICS")]
        if "GET_LINEAGE" in text:
            if self.lineage is None:
                raise RuntimeError("GET_LINEAGE needs Enterprise edition")
            return self.lineage
        if "FROM SEMANTIC_VIEW(" in text:
            if self.fail_query:
                raise RuntimeError("semantic view rejected the query")
            return self.answer
        if "GLOSSARY WHERE metric_name" in text:
            entry = self.glossary.get(params[0])
            return [Row(ENTRY=json.dumps(entry))] if entry else []
        if "GLOSSARY" in text:
            return [Row(METRIC_NAME=name) for name in self.glossary]
        return []

    def audit_rows(self):
        return [json.loads(params[0]) for text, params in self.statements if "AUDIT.ANSWERS" in text]

    def audited_into(self):
        return {text.split("INSERT INTO ", 1)[1].split(" ", 1)[0] for text, _ in self.statements
                if text.startswith("INSERT INTO")}


ON_TIME_FY2026 = json.dumps({"metrics": ["on_time_delivery"], "time": {"range": "fy2026"}})


def test_an_answer_carries_the_persona_role_view_hash_and_one_audit_row():
    ledger = Ledger()
    answer = governed_query.run(ledger, "logistics_sv_v1", ON_TIME_FY2026, "On-time delivery in FY2026?")
    assert answer["view"] == "LOGISTICS_SV_V1" and answer["role"] == "LOGISTICS_ROLE"
    assert answer["rows"] == [{"on_time_delivery": 0.837553}] and answer["row_count"] == 1
    assert answer["semantic_query_hash"] and "SCM_DEV.SEMANTIC.LOGISTICS_SV_V1" in answer["sql"]
    assert answer["metrics"][0]["status"] == "approved"
    [audit] = ledger.audit_rows()
    assert audit["hash"] == answer["semantic_query_hash"] and audit["refusal"] is None


def test_a_session_without_a_database_answers_from_the_database_the_procedure_was_created_in():
    ledger = Ledger(database=None)
    answer = governed_query.run(ledger, "LOGISTICS_SV_V1", ON_TIME_FY2026, "", db="SCM_TEST")
    assert "SCM_TEST.SEMANTIC.LOGISTICS_SV_V1" in answer["sql"]
    assert ledger.audited_into() == {"SCM_TEST.AUDIT.ANSWERS"}


def test_the_same_question_hashes_the_same_on_every_persona_view():
    hashes = {governed_query.run(Ledger(), view, ON_TIME_FY2026)["semantic_query_hash"]
              for view in ("LOGISTICS_SV_V1", "PLANNING_SV_V1", "SCM_GOVERNED_V1")}
    assert len(hashes) == 1


def test_a_view_outside_the_governed_set_is_refused_and_the_refusal_is_audited():
    ledger = Ledger()
    assert governed_query.run(ledger, "CONFORMED.FCT_PO_LINE", ON_TIME_FY2026)["error"] == "unknown_view"
    assert [a["refusal"] for a in ledger.audit_rows()] == ["unknown_view"]


@pytest.mark.parametrize("query, code", [("not json", "bad_query"), ("[1, 2]", "bad_query"),
                                         (json.dumps({"metrics": ["otif"], "dimensions": ["supplier_unit_cost"]}),
                                          "unknown_dimensions")])
def test_a_malformed_or_unreachable_query_is_refused_with_its_reason(query, code):
    ledger = Ledger()
    assert governed_query.run(ledger, "LOGISTICS_SV_V1", query)["error"] == code
    assert [a["refusal"] for a in ledger.audit_rows()] == [code]


def test_a_metric_the_persona_view_does_not_expose_is_refused_with_suggestions():
    ledger = Ledger(metrics=("otif",))
    refusal = governed_query.run(ledger, "LOGISTICS_SV_V1", ON_TIME_FY2026)
    assert refusal["error"] == "unknown_metrics"
    assert [a["refusal"] for a in ledger.audit_rows()] == ["unknown_metrics"]


def test_a_query_the_semantic_view_rejects_returns_its_sql_and_is_audited_as_failed():
    ledger = Ledger(fail_query=True)
    failure = governed_query.run(ledger, "LOGISTICS_SV_V1", ON_TIME_FY2026)
    assert failure["error"] == "query_failed" and "SEMANTIC_VIEW(" in failure["sql"]
    assert [a["refusal"] for a in ledger.audit_rows()] == ["query_failed"]


def test_rows_past_the_cap_are_cut_and_marked_truncated(monkeypatch):
    monkeypatch.setattr(governed_query, "ROW_CAP", 2)
    ledger = Ledger(answer=[Row(ON_TIME_DELIVERY=v) for v in (0.81, 0.83, 0.85)])
    answer = governed_query.run(ledger, "LOGISTICS_SV_V1", ON_TIME_FY2026)
    assert answer["truncated"] and answer["row_count"] == 2


def test_on_standard_edition_lineage_falls_back_to_the_registry_path_and_says_so():
    lineage = explain_lineage.run(Ledger(), "on_time_delivery")
    assert lineage["source"].startswith("registry (GET_LINEAGE unavailable")
    layers = {step["layer"]: step for step in lineage["path"]}
    assert layers["conformed"]["objects"] == ["fct_sales_order_line"]
    assert layers["semantic"]["columns"] == ["is_delivered", "is_on_time"]


def test_with_the_lineage_graph_each_upstream_object_lands_in_its_layer():
    edges = [Row(s="RAW", sn="SALES_ORDERS", t="STAGING", tn="STG_SALES_ORDERS", d=2),
             Row(s="STAGING", sn="STG_SALES_ORDERS", t="CONFORMED", tn="FCT_SALES_ORDER_LINE", d=1)]
    lineage = explain_lineage.run(Ledger(lineage=edges), "on_time_delivery", db="SCM_PROD")
    layers = {step["layer"]: step["objects"] for step in lineage["path"]}
    assert lineage["source"] == "Snowflake lineage graph"
    assert layers["source"] == ["sales_orders"] and layers["staging"] == ["stg_sales_orders"]


def test_lineage_for_a_name_outside_the_registry_suggests_the_nearest_metric():
    refusal = explain_lineage.run(Ledger(), "on_time_delivry")
    assert refusal["error"] == "unknown_metrics" and "on_time_delivery" in refusal["suggestions"]["on_time_delivry"]


def test_describe_metric_reads_the_glossary_entry_of_its_own_database():
    entry = {"name": "otif", "title": "On time in full"}
    ledger = Ledger(database=None, glossary={"otif": entry})
    assert describe_metric.run(ledger, " OTIF ", db="SCM_DEV") == entry
    assert ledger.statements[0][0].startswith("SELECT entry FROM SCM_DEV.SEMANTIC.GLOSSARY")


def test_describe_metric_for_an_unknown_name_suggests_from_the_glossary():
    ledger = Ledger(glossary={"otif": {"name": "otif"}, "unit_fill_rate": {"name": "unit_fill_rate"}})
    refusal = describe_metric.run(ledger, "otf")
    assert refusal["error"] == "unknown_metrics" and refusal["suggestions"]["otf"][0] == "otif"
