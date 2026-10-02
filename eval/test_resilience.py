"""Suite 5: probes, the model-free path, limits, rollback and the stale-source alert.
Time Travel restore and the SPCS probe history need the account and are marked so."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def client(tmp_path_factory, warehouse):
    os.environ.update(SCM_BACKEND="local", SCM_AGENT="off", SCM_RATE_PER_MINUTE="1000",
                      SCM_STATE_DIR=str(tmp_path_factory.mktemp("resilience")))
    from api import backend
    from api.main import app

    backend.set_backend(None)
    with TestClient(app) as c:
        yield c
    backend.set_backend(None)


def test_readiness_and_liveness_answer(client):
    assert client.get("/health").json()["status"] == "ready"
    assert client.get("/live").json()["status"] == "alive"


def test_readiness_fails_closed_when_the_backend_cannot_answer(client, monkeypatch):
    from api import backend

    class Broken:
        mode = "local"

        def health(self):
            raise ConnectionError("warehouse suspended")

    monkeypatch.setattr(backend, "_backend", Broken())
    assert client.get("/health").status_code == 503
    assert client.get("/live").status_code == 200


def test_the_builder_answers_with_the_model_switched_off(client):
    answer = client.post("/api/query", json={"query": {"metrics": ["otif"], "time": {"range": "q3"}}}).json()
    assert answer["path"] == "builder" and answer["rows"]


def test_ask_degrades_instead_of_failing_when_the_agent_is_unreachable(client, monkeypatch):
    monkeypatch.setenv("SCM_AGENT", "on")
    monkeypatch.delenv("SNOWFLAKE_HOST", raising=False)
    answer = client.post("/api/ask", json={"question": "What is fill rate by plant?"}).json()
    assert answer["degraded"] is True and "SNOWFLAKE_HOST" in answer["degraded_reason"]
    assert answer["metric_name"] == "unit_fill_rate"


def test_row_cap_and_statement_timeout_are_set_where_queries_run():
    from api.backend import ROW_CAP

    source = (ROOT / "snowflake" / "procs" / "governed_query.py").read_text()
    assert ROW_CAP == 10_000 and "ROW_CAP = 10_000" in source
    assert "STATEMENT_TIMEOUT_IN_SECONDS" in source
    assert re.search(r"query_timeout: 30", (ROOT / "snowflake" / "agent" / "create_agent.sql").read_text())


def test_a_rollback_is_the_previous_version_compiled_again():
    import compile as compiler

    forward = compiler.versioning_sql("prod", 2)
    back = compiler.versioning_sql("prod", 1)
    assert "GRANT SELECT ON SEMANTIC VIEW SCM_PROD.SEMANTIC.PLANNING_SV_V2 TO ROLE PLANNING_ROLE" in forward
    assert "REVOKE SELECT ON SEMANTIC VIEW SCM_PROD.SEMANTIC.PLANNING_SV_V1 FROM ROLE PLANNING_ROLE" in forward
    assert "GRANT SELECT ON SEMANTIC VIEW SCM_PROD.SEMANTIC.PLANNING_SV_V1 TO ROLE PLANNING_ROLE" in back
    assert "V2" not in back


def test_rolling_back_restores_the_previous_answers(registry, warehouse, tmp_path):
    import semantic

    query = {"metrics": ["on_time_delivery"], "time": {"range": "fy2026"}}
    before = semantic.execute_local(warehouse, registry, query)
    changed = yaml.safe_load((ROOT / "ontology" / "metrics.yaml").read_text())
    changed["metrics"]["on_time_delivery"]["semantic"]["expr"] = (
        "SUM(delivered_lines.is_on_time_to_request) / NULLIF(SUM(delivered_lines.is_delivered), 0)")
    changed["metrics"]["on_time_delivery"]["version"] = 2
    v2_path = tmp_path / "metrics.yaml"
    v2_path.write_text(yaml.safe_dump(changed))
    after = semantic.execute_local(warehouse, semantic.load_registry(v2_path), query)
    restored = semantic.execute_local(warehouse, semantic.load_registry(), query)
    assert after["rows"] != before["rows"]
    assert restored["rows"] == before["rows"] and restored["semantic_query_hash"] == before["semantic_query_hash"]


def test_a_stale_source_is_flagged_the_way_the_alert_fires(client):
    stale_after = 6 * 3600
    alert = (ROOT / "snowflake" / "setup" / "08_alerts.sql").read_text()
    assert "TIMESTAMPDIFF(HOUR, last_loaded_at, CURRENT_TIMESTAMP()) > 6" in alert
    for f in (ROOT / "data" / "out" / "tms").glob("*.parquet"):
        old = f.stat().st_mtime - stale_after - 60
        os.utime(f, (old, old))
    status = client.get("/api/status").json()
    tms = next(s for s in status["freshness"] if s["source"] == "tms")
    assert tms["stale"] is True
    assert not next(s for s in status["freshness"] if s["source"] == "erp")["stale"]
    for f in (ROOT / "data" / "out" / "tms").glob("*.parquet"):
        os.utime(f, None)


@pytest.mark.skipif(os.getenv("SCM_BACKEND") != "snowflake", reason="needs account: Time Travel clone and UNDROP")
def test_restore_from_a_time_travel_clone_matches_the_original():
    import snowflake.connector

    with snowflake.connector.connect(connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME", "scm_test")) as conn:
        cur = conn.cursor()
        cur.execute("CREATE OR REPLACE TABLE SCM_TEST.CONFORMED.FCT_PO_LINE_RESTORED CLONE SCM_TEST.CONFORMED.FCT_PO_LINE "
                    "AT (OFFSET => -60)")
        cur.execute("SELECT (SELECT HASH_AGG(*) FROM SCM_TEST.CONFORMED.FCT_PO_LINE) = "
                    "(SELECT HASH_AGG(*) FROM SCM_TEST.CONFORMED.FCT_PO_LINE_RESTORED)")
        assert cur.fetchone()[0]
        cur.execute("DROP TABLE SCM_TEST.CONFORMED.FCT_PO_LINE_RESTORED")
