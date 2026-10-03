import argparse
import base64
import hashlib
import json
import os
import sys
import time

import httpx
import jwt
from cryptography.hazmat.primitives import serialization

CHECK_USERS = {"procurement": "STRATA_CHECK_PROCUREMENT", "logistics": "STRATA_CHECK_LOGISTICS",
               "emea": "STRATA_CHECK_EMEA"}
PAGES = ["/api/personas", "/api/meta", "/api/glossary", "/api/status", "/api/audit", "/api/governance",
         "/api/operations", "/api/lineage/on_time_delivery"]


# Key-pair JWT exchanged at /oauth/token for a token scoped to the endpoint host (SPCS docs).
# The private key stays outside the repository; STRATA_CHECK_KEY points at it.
def endpoint_token(account: str, locator: str, user: str, host: str, key_path: str) -> str:
    with open(key_path, "rb") as fh:
        key = serialization.load_pem_private_key(fh.read(), password=None)
    der = key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    fingerprint = "SHA256:" + base64.b64encode(hashlib.sha256(der).digest()).decode()
    qualified = f"{locator.upper()}.{user}"
    now = int(time.time())
    assertion = jwt.encode({"iss": f"{qualified}.{fingerprint}", "sub": qualified, "iat": now, "exp": now + 3000},
                           key, algorithm="RS256")
    r = httpx.post(f"https://{account.lower()}.snowflakecomputing.com/oauth/token", timeout=60,
                   data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "scope": host,
                         "assertion": assertion})
    r.raise_for_status()
    return r.text


def session(account: str, locator: str, user: str, host: str, key_path: str) -> httpx.Client:
    token = endpoint_token(account, locator, user, host, key_path)
    return httpx.Client(base_url=f"https://{host}", timeout=300,
                        headers={"Authorization": f'Snowflake Token="{token}"'})


def query(client: httpx.Client, metrics: list[str], dimensions: list[str]) -> dict:
    r = client.post("/api/query", json={"query": {"metrics": metrics, "dimensions": dimensions,
                                                  "time": {"range": "fy2026"}}})
    r.raise_for_status()
    return r.json()


def column(answer: dict, name: str) -> list:
    return [row.get(name) for row in answer.get("rows", [])]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--account", required=True)
    p.add_argument("--locator", required=True, help="account locator; the JWT names it, not the org-account")
    p.add_argument("--host", required=True)
    p.add_argument("--ask", action="store_true", help="also run one Ask through the agent")
    args = p.parse_args()
    key_path = os.environ["STRATA_CHECK_KEY"]
    failures: list[str] = []

    def check(ok: bool, label: str) -> None:
        print(("pass  " if ok else "FAIL  ") + label)
        if not ok:
            failures.append(label)

    clients = {persona: session(args.account, args.locator, user, args.host, key_path) for persona, user in CHECK_USERS.items()}
    expected = {"procurement": "PROCUREMENT_ROLE", "logistics": "LOGISTICS_ROLE", "emea": "EMEA_PLANNING_ROLE"}

    for path in PAGES:
        r = clients["procurement"].get(path)
        check(r.status_code == 200 and len(r.content) > 2, f"{path} {r.status_code}")
    check(clients["procurement"].get("/").status_code == 200, "web shell /")
    # The home panel: three legacy numbers on RAW against the governed one.
    story = clients["procurement"].post("/api/before-after", json={"window": "fy2026"})
    check(story.status_code == 200 and len(story.json().get("legacy", [])) == 3, f"/api/before-after {story.status_code}")

    for persona, client in clients.items():
        body = client.get("/api/personas").json()
        check(body["pinned"] and body["default"] == expected[persona], f"{persona} pinned to {body['default']}")

    emea = query(clients["emea"], ["on_time_delivery"], ["region"])
    regions = sorted({str(v) for v in column(emea, "region")})
    check(regions == ["EMEA"] and emea.get("role") == "EMEA_PLANNING_ROLE", f"EMEA user regions {regions}")

    # No governed metric reads supplier_unit_cost, so the API refuses it for every persona; the
    # procurement-reads-it control runs on the account in suite 4. Here: logistics gets no value.
    r = clients["logistics"].post("/api/query", json={"query": {"metrics": ["landed_cost_per_unit"],
                                                                "dimensions": ["supplier_unit_cost"],
                                                                "time": {"range": "fy2026"}}})
    leaked = [v for v in column(r.json(), "supplier_unit_cost") if v is not None] if r.status_code == 200 else []
    check(not leaked, f"logistics reads no supplier unit cost ({r.status_code}, {len(leaked)} values)")

    if args.ask:
        started = time.perf_counter()
        r = clients["logistics"].post("/api/ask", json={"question": "What was on-time delivery in FY2026?"})
        body = r.json()
        check(r.status_code == 200 and body.get("path") == "agent" and body.get("role") == "LOGISTICS_ROLE" and "LOGISTICS" in str(body.get("view")),
              f"Ask as logistics: role {body.get('role')}, view {body.get('view')}, path {body.get('path')}, "
              f"{time.perf_counter() - started:.1f}s")

    print(json.dumps({"failures": failures}))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
