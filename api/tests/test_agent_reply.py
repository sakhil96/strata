from __future__ import annotations

import json
import logging

import httpx
import pytest

from api import agent

LEDGER_ROW = {"semantic_query_hash": "c0e0370d", "metric_name": "on_time_delivery", "role": "SCM_SPCS_ROLE"}


def tool_result(name, status, *parts):
    return {"type": "tool_result", "tool_result": {"name": name, "status": status, "content": list(parts)}}


def test_a_procedure_result_wrapped_as_json_text_is_read_as_the_answer_contract():
    reply = {"content": [{"type": "text", "text": "Read as on-time delivery for FY2026."},
                         tool_result("GOVERNED_QUERY", "success",
                                     {"type": "json", "json": {"execution_type": "procedure",
                                                               "result": json.dumps(LEDGER_ROW)}})]}
    parsed = agent.parse(reply)
    assert parsed["answer"] == LEDGER_ROW and parsed["refusal"] is None
    assert parsed["narrative"] == "Read as on-time delivery for FY2026."


def test_results_from_other_tools_and_non_contracts_are_not_answers():
    reply = {"content": [tool_result("DESCRIBE_METRIC", "success", {"type": "json", "json": LEDGER_ROW}),
                         tool_result("GOVERNED_QUERY", "success", {"type": "text", "text": "not json"},
                                     {"type": "text", "text": json.dumps({"error": "unknown_view"})})]}
    assert agent.parse(reply)["answers"] == []


def test_a_reply_without_a_governed_answer_logs_each_tool_and_its_error_but_no_rows(caplog):
    failed = tool_result("GOVERNED_QUERY", "error",
                         {"type": "text", "text": "{'error': 'Python Interpreter Error: NoneType has no attribute strip'}"})
    with caplog.at_level(logging.INFO, logger="strata.agent"):
        agent.parse({"content": [failed, tool_result("EXPLAIN_LINEAGE", "success", {"type": "json", "json": {"rows": [1]}})]})
    [record] = [r for r in caplog.records if r.getMessage() == "agent_no_governed_answer"]
    assert record.tools == [{"name": "GOVERNED_QUERY", "status": "error",
                             "error": "{'error': 'Python Interpreter Error: NoneType has no attribute strip'}"},
                            {"name": "EXPLAIN_LINEAGE", "status": "success", "error": ""}]


@pytest.mark.parametrize("text, refused", [("I can't answer supplier bank details.", True),
                                           ("That request cannot be answered from governed metrics.", True),
                                           ("On-time delivery was 83.8% in FY2026.", False)])
def test_a_refusal_is_recognised_only_when_the_agent_says_so_and_ran_no_governed_query(text, refused):
    assert (agent.parse({"content": [{"type": "text", "text": text}]})["refusal"] == "agent_refused") is refused


def test_without_a_host_the_agent_is_unavailable(monkeypatch):
    monkeypatch.delenv("SNOWFLAKE_HOST", raising=False)
    with pytest.raises(agent.AgentUnavailable, match="SNOWFLAKE_HOST"):
        agent.run("On-time delivery in FY2026?", "LOGISTICS_ROLE", "STRATA_CHECK_LOGISTICS", None, None)


def test_without_a_token_key_or_pat_the_agent_is_unavailable(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_HOST", "account.snowflakecomputing.com")
    for name in ("SNOWFLAKE_PRIVATE_KEY_PATH", "SNOWFLAKE_PAT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(agent.Path, "exists", lambda self: False)
    with pytest.raises(agent.AgentUnavailable, match="no service token"):
        agent.run("On-time delivery in FY2026?", "LOGISTICS_ROLE", "STRATA_CHECK_LOGISTICS", None, None)


def test_the_run_names_the_persona_and_the_signed_in_user_and_parses_the_reply(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_HOST", "account.snowflakecomputing.com")
    monkeypatch.setenv("SCM_ENV", "test")
    monkeypatch.setenv("SNOWFLAKE_PAT", "pat-for-the-test")
    monkeypatch.setattr(agent.Path, "exists", lambda self: False)
    sent = {}

    def post(url, json, headers, timeout):
        sent.update(url=url, body=json, headers=headers)
        reply = {"content": [tool_result("GOVERNED_QUERY", "success", {"type": "json", "json": LEDGER_ROW})]}
        return httpx.Response(200, json=reply, request=httpx.Request("POST", url))

    monkeypatch.setattr(agent.httpx, "post", post)
    parsed = agent.run("On-time delivery in FY2026?", "LOGISTICS_ROLE", "STRATA_CHECK_LOGISTICS", 7, 3)
    assert sent["url"].endswith("/databases/SCM_TEST/schemas/AGENT/agents/SCM_AGENT:run")
    assert sent["body"]["messages"][0]["content"][0]["text"].startswith("[persona=LOGISTICS_ROLE]")
    assert sent["body"]["thread_id"] == 7 and sent["body"]["parent_message_id"] == 3
    assert sent["headers"]["Sf-Context-Current-User"] == "STRATA_CHECK_LOGISTICS"
    assert sent["headers"]["X-Snowflake-Authorization-Token-Type"] == "PROGRAMMATIC_ACCESS_TOKEN"
    assert parsed["answer"] == LEDGER_ROW


def test_a_failed_agent_call_is_reported_as_unavailable_without_the_response_body(monkeypatch):
    monkeypatch.setenv("SNOWFLAKE_HOST", "account.snowflakecomputing.com")
    monkeypatch.setenv("SNOWFLAKE_PAT", "pat-for-the-test")
    monkeypatch.setattr(agent.Path, "exists", lambda self: False)
    monkeypatch.setattr(agent.httpx, "post", lambda url, **kw: httpx.Response(
        401, text="token detail", request=httpx.Request("POST", url)))
    with pytest.raises(agent.AgentUnavailable) as raised:
        agent.run("On-time delivery in FY2026?", "LOGISTICS_ROLE", "STRATA_CHECK_LOGISTICS", None, None)
    assert "token detail" not in str(raised.value)
