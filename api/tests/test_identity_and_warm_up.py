from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api import main
from api.routes import deps

ON_TIME = {"query": {"metrics": ["on_time_delivery"], "time": {"range": "fy2026"}}}


class ColdLedger:
    warm = False

    def health(self):
        raise ConnectionError("session not open")

    def legacy_otd(self, window):
        raise ConnectionError("session not open")


@pytest.fixture
def quiet_client(client):
    return TestClient(main.app, raise_server_exceptions=False)


def test_an_unmapped_signed_in_user_chooses_any_persona_on_the_dial(client):
    for persona in ("PLANNING_ROLE", "EMEA_PLANNING_ROLE", "JUDGE_ROLE"):
        body = client.post("/api/query", json=ON_TIME | {"persona": persona},
                           headers={"Sf-Context-Current-User": "ADMIN_USER"}).json()
        assert body["role"] == persona


def test_a_mapped_user_stays_pinned_whatever_the_dial_sends(client, monkeypatch):
    monkeypatch.setenv("SCM_USER_PERSONAS", '{"STRATA_CHECK_LOGISTICS": "LOGISTICS_ROLE"}')
    deps.user_personas.cache_clear()
    try:
        body = client.post("/api/query", json=ON_TIME | {"persona": "PROCUREMENT_ROLE"},
                           headers={"Sf-Context-Current-User": "strata_check_logistics"}).json()
        assert body["role"] == "LOGISTICS_ROLE"
    finally:
        deps.user_personas.cache_clear()


def test_a_broken_persona_mapping_refuses_with_403_and_a_message_not_500(client, monkeypatch):
    monkeypatch.setenv("SCM_USER_PERSONAS", '{"STRATA_CHECK_LOGISTICS": "ACCOUNTADMIN"}')
    deps.user_personas.cache_clear()
    try:
        response = client.get("/api/personas", headers={"Sf-Context-Current-User": "ADMIN_USER"})
        assert response.status_code == 403 and "persona" in response.json()["message"]
    finally:
        deps.user_personas.cache_clear()


def test_before_the_first_session_opens_data_routes_answer_503_with_retry_after(quiet_client, monkeypatch):
    monkeypatch.setattr(main, "get_backend", lambda: ColdLedger())
    monkeypatch.setattr(deps, "get_backend", lambda: ColdLedger())
    response = quiet_client.post("/api/before-after", json={"window": "fy2026"})
    assert response.status_code == 503 and response.headers["Retry-After"] == str(main.WAKE_RETRY_S)
    assert response.json()["error"] == "waking" and response.json()["request_id"]
    health = quiet_client.get("/health")
    assert health.status_code == 503 and health.json()["session"] == "waking"


def test_a_failure_after_warm_up_is_a_500_that_keeps_the_request_id(quiet_client, monkeypatch):
    class WarmLedger(ColdLedger):
        warm = True

    monkeypatch.setattr(main, "get_backend", lambda: WarmLedger())
    monkeypatch.setattr(deps, "get_backend", lambda: WarmLedger())
    body = quiet_client.post("/api/before-after", json={"window": "fy2026"}).json()
    assert body["error"] == "internal_error" and body["request_id"]
    assert body["message"] == "Something failed on our side. Try again in a minute; quote this id if it persists."


def test_liveness_never_depends_on_the_snowflake_session(quiet_client, monkeypatch):
    monkeypatch.setattr(main, "get_backend", lambda: ColdLedger())
    assert quiet_client.get("/live").status_code == 200
