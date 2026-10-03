"""Build eval/governance_snapshot.json from the committed SQL: the grants the setup files make and
the policies, for any environment (every database is written {{DB}}). CI diffs SHOW GRANTS on the account
against this file. The agent card is not here: the API reads it from DESCRIBE AGENT, so a page
never names an agent or model that is not deployed."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "governance_snapshot.json"
GRANT = re.compile(r"^GRANT\s+(.+?)\s+ON\s+(.+?)\s+TO\s+ROLE\s+(\w+)\s*;", re.I | re.M)
ROLE_GRANT = re.compile(r"^GRANT\s+ROLE\s+(\w+)\s+TO\s+(?:ROLE|USER)\s+(\w+)\s*;", re.I | re.M)


def grants() -> list[dict]:
    rows = set()
    for path in sorted((ROOT / "snowflake").rglob("*.sql")):
        if "semantic" in path.parts and path.name != "versioning.sql":
            continue
        text = re.sub(r"\bSCM_(DEV|TEST|PROD)\b", "{{DB}}", path.read_text())
        for privilege, obj, role in GRANT.findall(text):
            if privilege.upper().startswith("ROLE "):
                continue
            rows.add((role.upper(), re.sub(r"\s+", " ", privilege.upper()), re.sub(r"\s+", " ", obj)))
        for granted, grantee in ROLE_GRANT.findall(text):
            rows.add((grantee.upper(), "ROLE", granted.upper()))
    return [{"role": r, "privilege": p, "object": o} for r, p, o in sorted(rows)]


def policies() -> list[dict]:
    compiled = ROOT / "snowflake" / "policies"
    found = []
    for name in re.findall(r"CREATE OR REPLACE SECURE VIEW \S+\.SEMANTIC_BASE\.(\w+)",
                           (compiled / "standard" / "secure_views.sql").read_text()):
        found.append({"name": f"SEMANTIC_BASE.{name}", "kind": "secure view (Standard edition)",
                      "applies_to": "rows by GOV.ENTITLEMENTS, governed columns by entitlements.yaml"})
    for kind, name in re.findall(r"CREATE OR REPLACE (MASKING POLICY|ROW ACCESS POLICY) \S+\.GOV\.(\w+)",
                                 (compiled / "enterprise" / "policies.sql").read_text()):
        applies = "one governed column, per entitlements.yaml" if kind == "MASKING POLICY" else "plant_id on the conformed facts"
        found.append({"name": name, "kind": f"{kind.lower()} (Enterprise edition)", "applies_to": applies})
    return found


def main() -> None:
    snapshot = {"source": "committed SQL in snowflake/", "grants": grants(), "policies": policies()}
    OUT.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(snapshot['grants'])} grants, {len(snapshot['policies'])} policies")


if __name__ == "__main__":
    main()
