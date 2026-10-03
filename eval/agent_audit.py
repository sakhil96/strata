"""Ask SCM_AGENT through agent:run and reconcile every number it reports with AUDIT.ANSWERS.

Each question runs in its own thread. The agent rewrites the question it passes on, so the join
key is the semantic_query_hash: a reply reconciles when every GOVERNED_QUERY hash in it has an
AUDIT.ANSWERS row written by the same user while that thread was running. A reply is numeric when
its prose carries a figure, and a numeric reply with no GOVERNED_QUERY result is a bypass.
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from api import agent  # noqa: E402

FIGURE = re.compile(r"\d+(\.\d+)?\s*(%|percent|days|hours|usd|\$)|\$\s?\d|\b0\.\d{2,}\b|\b\d{2,}\.\d+\b", re.I)


@dataclass
class Reply:
    question: str
    thread_id: int
    status: int
    narrative: str = ""
    hashes: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    refused: bool = False
    seconds: float = 0.0
    started_at: float = 0.0

    @property
    def numeric(self) -> bool:
        return bool(FIGURE.search(self.narrative))


def _headers() -> dict[str, str]:
    kind, token = agent._token()
    return {"Authorization": f"Bearer {token}", "X-Snowflake-Authorization-Token-Type": kind,
            "Content-Type": "application/json", "Accept": "application/json"}


def ask(host: str, db: str, question: str) -> Reply:
    thread = httpx.post(f"https://{host}/api/v2/cortex/threads", json={"origin_application": "strata_eval"},
                        headers=_headers(), timeout=60)
    thread.raise_for_status()
    thread_id = int(thread.json()["thread_id"])
    started = time.time()
    resp = httpx.post(
        f"https://{host}/api/v2/databases/{db}/schemas/AGENT/agents/SCM_AGENT:run",
        json={"thread_id": thread_id, "parent_message_id": 0, "stream": False,
              "messages": [{"role": "user", "content": [{"type": "text", "text": question}]}]},
        headers=_headers(), timeout=240)
    reply = Reply(question, thread_id, resp.status_code, seconds=round(time.time() - started, 1), started_at=started)
    if resp.status_code != 200:
        reply.narrative = resp.text[:500]
        return reply
    payload = resp.json()
    reply.tools = [item["tool_use"].get("name", "") for item in payload.get("content", []) if item.get("type") == "tool_use"]
    reply.hashes = [r["semantic_query_hash"] for r in agent.governed_results(payload)]
    parsed = agent.parse(payload)
    reply.narrative = parsed["narrative"]
    reply.refused = bool(parsed["refusal"]) or (not reply.hashes and not reply.numeric)
    return reply


def audited(cursor: Any, db: str, user: str, reply: Reply) -> set[str]:
    cursor.execute(
        f"SELECT semantic_query_hash FROM {db}.AUDIT.ANSWERS WHERE username = %s AND semantic_query_hash IS NOT NULL "
        "AND ts BETWEEN TO_TIMESTAMP_LTZ(%s) AND TO_TIMESTAMP_LTZ(%s)",
        (user.upper(), int(reply.started_at) - 5, int(reply.started_at + reply.seconds) + 5))
    return {row[0] for row in cursor.fetchall()}


def reconcile(replies: list[Reply], cursor: Any, db: str, user: str) -> list[dict[str, Any]]:
    rows = []
    for r in replies:
        in_audit = audited(cursor, db, user, r)
        rows.append({
            "question": r.question, "thread_id": r.thread_id, "status": r.status, "seconds": r.seconds,
            "tools": r.tools, "numeric": r.numeric, "refused": r.refused,
            "hashes": r.hashes, "audited_hashes": sorted(in_audit),
            "reconciled": (not r.numeric) or (bool(r.hashes) and set(r.hashes) <= in_audit),
        })
    return rows
