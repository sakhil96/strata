"""Calls the Cortex Agent through agent:run and pulls the governed answer out of its tool results."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import httpx

TIMEOUT_S = float(os.getenv("SCM_AGENT_TIMEOUT_S", "20"))


class AgentUnavailable(RuntimeError):
    pass


def enabled() -> bool:
    return os.getenv("SCM_AGENT", "off") == "on"


def _keypair_jwt(account: str, user: str, key_path: str) -> str:
    import base64
    import hashlib
    import time

    import jwt
    from cryptography.hazmat.primitives import serialization

    key = serialization.load_pem_private_key(Path(key_path).read_bytes(), password=None)
    der = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    fingerprint = "SHA256:" + base64.b64encode(hashlib.sha256(der).digest()).decode()
    qualified = f"{account.upper()}.{user.upper()}"
    now = int(time.time())
    return jwt.encode({"iss": f"{qualified}.{fingerprint}", "sub": qualified, "iat": now, "exp": now + 3000},
                      key, algorithm="RS256")


def _token() -> tuple[str, str]:
    session = Path("/snowflake/session/token")
    if session.exists():
        return "OAUTH", session.read_text()
    # Outside SPCS the service user signs its own JWT, so no long-lived token sits in the environment.
    key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
    if key_path and os.getenv("SNOWFLAKE_ACCOUNT") and os.getenv("SNOWFLAKE_USER"):
        return "KEYPAIR_JWT", _keypair_jwt(os.environ["SNOWFLAKE_ACCOUNT"], os.environ["SNOWFLAKE_USER"], key_path)
    token = os.getenv("SNOWFLAKE_PAT")
    if not token:
        raise AgentUnavailable("no service token, key pair or PAT available to call the agent")
    return "PROGRAMMATIC_ACCESS_TOKEN", token


def run(question: str, role: str, user: str, thread_id: int | None, parent_message_id: int | None) -> dict[str, Any]:
    host = os.getenv("SNOWFLAKE_HOST")
    if not host:
        raise AgentUnavailable("SNOWFLAKE_HOST is not set")
    db = f"SCM_{os.getenv('SCM_ENV', 'dev').upper()}"
    kind, token = _token()
    body: dict[str, Any] = {
        "messages": [{"role": "user", "content": [{"type": "text", "text": f"[persona={role}] {question}"}]}],
        "stream": False,
    }
    if thread_id is not None:
        body |= {"thread_id": thread_id, "parent_message_id": parent_message_id or 0}
    headers = {"Authorization": f"Bearer {token}", "X-Snowflake-Authorization-Token-Type": kind,
               "Content-Type": "application/json", "Accept": "application/json",
               "Sf-Context-Current-User": user}
    try:
        resp = httpx.post(f"https://{host}/api/v2/databases/{db}/schemas/AGENT/agents/SCM_AGENT:run",
                          json=body, headers=headers, timeout=TIMEOUT_S)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        raise AgentUnavailable(f"agent call failed: {exc.__class__.__name__}") from exc
    return parse(resp.json())


def parse(payload: dict[str, Any]) -> dict[str, Any]:
    """The answer contract is whatever GOVERNED_QUERY returned; the agent's prose rides alongside."""
    governed, prose, refusal = None, [], None
    for item in payload.get("content", []):
        if item.get("type") == "text":
            prose.append(item.get("text", ""))
        if item.get("type") == "tool_result":
            result = item.get("tool_result", {})
            if result.get("name") != "GOVERNED_QUERY":
                continue
            for part in result.get("content", []):
                data = part.get("json") or (json.loads(part["text"]) if part.get("type") == "text" else None)
                if isinstance(data, dict) and "semantic_query_hash" in data:
                    governed = data
    text = "\n".join(prose).strip()
    if governed is None and text.lower().startswith(("i can't", "i cannot", "refus")):
        refusal = "agent_refused"
    return {"answer": governed, "narrative": text, "refusal": refusal}
