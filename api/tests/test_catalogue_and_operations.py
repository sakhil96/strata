from __future__ import annotations


def test_meta_lists_every_governed_metric_with_reachable_dimensions(client):
    meta = client.get("/api/meta").json()
    names = {m["name"] for m in meta["metrics"]}
    assert {"on_time_delivery", "otif", "unit_fill_rate", "days_of_inventory", "landed_cost_per_unit"} <= names
    doi = next(m for m in meta["metrics"] if m["name"] == "days_of_inventory")
    assert "segment" not in doi["dimensions"]


def test_glossary_entries_name_owner_steward_version_and_status(client):
    for entry in client.get("/api/glossary").json():
        assert entry["owner"] and entry["steward"] and entry["version"] and entry["status"] == "approved"


def test_lineage_walks_from_source_files_to_the_semantic_metric(client):
    lineage = client.get("/api/lineage/landed_cost_per_unit").json()
    layers = [step["layer"] for step in lineage["path"]]
    assert layers == ["source", "staging", "conformed", "semantic"]
    assert any("purchase_order_lines" in s for s in lineage["path"][0]["objects"])


def test_lineage_of_an_unknown_metric_is_a_404_with_suggestions(client):
    response = client.get("/api/lineage/landed_cost")
    assert response.status_code == 404
    assert "landed_cost_per_unit" in response.json()["suggestions"]["landed_cost"]


def test_probes_answer(client):
    assert client.get("/live").json() == {"status": "alive"}
    assert client.get("/health").json()["status"] == "ready"


def test_security_headers_are_on_every_response(client):
    for path in ("/live", "/api/meta"):
        headers = client.get(path).headers
        assert "max-age" in headers["strict-transport-security"]
        assert "frame-ancestors 'none'" in headers["content-security-policy"]
        script_src = next(d for d in headers["content-security-policy"].split(";") if d.strip().startswith("script-src"))
        assert "unsafe-inline" not in script_src and "unsafe-eval" not in script_src
        assert headers["x-content-type-options"] == "nosniff"
        assert headers["x-request-id"]


def test_rate_limit_answers_429_with_retry_after():
    from fastapi import HTTPException

    from api.security import RateLimiter

    limiter = RateLimiter(per_minute=2)
    limiter.check("PLANNER_A")
    limiter.check("PLANNER_A")
    try:
        limiter.check("PLANNER_A")
    except HTTPException as exc:
        assert exc.status_code == 429 and "Retry-After" in exc.headers
    else:
        raise AssertionError("third request inside a minute was allowed")
    limiter.check("PLANNER_B")


def test_unknown_persona_is_refused(client):
    response = client.get("/api/meta", headers={"x-persona": "ACCOUNTADMIN"})
    assert response.status_code == 422


def test_status_reports_freshness_for_each_source_system(client):
    status = client.get("/api/status").json()
    assert {f["source"] for f in status["freshness"]} == {"erp", "tms", "portal", "iot"}


def test_agent_reply_without_a_governed_tool_result_is_not_trusted():
    from api.agent import parse

    reply = parse({"content": [{"type": "text", "text": "OTD is about 90%."}]})
    assert reply["answer"] is None
    governed = parse({"content": [{"type": "tool_result", "tool_result": {
        "name": "GOVERNED_QUERY", "content": [{"type": "json", "json": {"semantic_query_hash": "abc", "rows": []}}]}}]})
    assert governed["answer"]["semantic_query_hash"] == "abc"


def test_inline_script_hashes_cover_exactly_the_inline_bodies():
    from api.security import inline_script_hashes

    html = b'<script src="/a.js"></script><script>self.__next_f.push(1)</script><script> </script>'
    assert len(inline_script_hashes(html)) == 1
