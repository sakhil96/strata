"""Build eval/governance_snapshot.json from the committed SQL: the agent's tools, the grants the
setup files make, and the policies. CI diffs SHOW GRANTS on the account against this file."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "governance_snapshot.json"
GRANT = re.compile(r"^GRANT\s+(.+?)\s+ON\s+(.+?)\s+TO\s+ROLE\s+(\w+)\s*;", re.I | re.M)
ROLE_GRANT = re.compile(r"^GRANT\s+ROLE\s+(\w+)\s+TO\s+(?:ROLE|USER)\s+(\w+)\s*;", re.I | re.M)


def agent() -> dict:
    sql = (ROOT / "snowflake" / "agent" / "create_agent.sql").read_text()
    spec = yaml.safe_load(re.search(r"FROM SPECIFICATION\s*\$\$(.*?)\$\$", sql, re.S).group(1)
                          .replace("{{DB}}", "SCM_PROD").replace("{{WH}}", "SCM_WH_PROD"))
    return {"name": "SCM_PROD.AGENT.SCM_AGENT", "model": spec["models"]["orchestration"],
            "tools": [{"name": t["tool_spec"]["name"], "type": t["tool_spec"]["type"],
                       "description": t["tool_spec"]["description"]} for t in spec["tools"]]}


def grants() -> list[dict]:
    rows = set()
    for path in sorted((ROOT / "snowflake").rglob("*.sql")):
        if "semantic" in path.parts and path.name != "versioning.sql":
            continue
        text = path.read_text().replace("{{DB}}", "SCM_PROD").replace("{{ENV}}", "PROD").replace("{{WH}}", "SCM_WH_PROD")
        for privilege, obj, role in GRANT.findall(text):
            if privilege.upper().startswith("ROLE "):
                continue
            rows.add((role.upper(), re.sub(r"\s+", " ", privilege.upper()), re.sub(r"\s+", " ", obj)))
        for granted, grantee in ROLE_GRANT.findall(text):
            rows.add((grantee.upper(), "ROLE", granted.upper()))
    return [{"role": r, "privilege": p, "object": o} for r, p, o in sorted(rows)]


def policies() -> list[dict]:
    text = (ROOT / "snowflake" / "setup" / "04_policies.sql").read_text()
    found = []
    for kind, name in re.findall(r"CREATE (MASKING POLICY|ROW ACCESS POLICY) IF NOT EXISTS \{\{DB\}\}\.CONFORMED\.(\w+)", text):
        applies = ("columns tagged CONFIDENTIAL or RESTRICTED through the SENSITIVITY tag" if kind == "MASKING POLICY"
                   else "plant_id on the five conformed facts, scoped by USER_PLANT_SCOPE")
        found.append({"name": name, "kind": kind.lower(), "applies_to": applies})
    return found


def main() -> None:
    snapshot = {"source": "committed SQL in snowflake/", "agent": agent(), "grants": grants(), "policies": policies()}
    OUT.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(snapshot['grants'])} grants, {len(snapshot['policies'])} policies")


if __name__ == "__main__":
    main()
