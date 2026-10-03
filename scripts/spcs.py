"""Deploy or roll back the STRATA SPCS service.

deploy: pushes the image tag, records it in OPS.IMAGE_VERSIONS, and alters the service
spec to the new tag. rollback: re-applies the previous recorded tag.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "snowflake" / "spcs" / "service_spec.yaml"
ENDPOINT_ROLES = ["PLANNING_ROLE", "PROCUREMENT_ROLE", "LOGISTICS_ROLE", "EXECUTIVE_ROLE", "EMEA_PLANNING_ROLE",
                  "JUDGE_ROLE"]


def snow_sql(sql: str, connection: str) -> str:
    return subprocess.run(["snow", "sql", "-q", sql, "-c", connection, "--role", "SCM_SPCS_ROLE", "--format", "csv"],
                          check=True, capture_output=True, text=True).stdout


def apply(env: str, tag: str, connection: str) -> None:
    db = f"SCM_{env.upper()}"
    spec = (SPEC.read_text().replace("{{TAG}}", tag).replace("{{DB_LOWER}}", db.lower())
            .replace("{{ENV_UPPER}}", env.upper()).replace("{{ENV}}", env))
    if "$$" in spec:
        raise SystemExit("service spec may not contain $$")
    exists = "STRATA_SERVICE" in snow_sql(f"SHOW SERVICES LIKE 'STRATA_SERVICE' IN SCHEMA {db}.AGENT", connection)
    if exists:
        snow_sql(f"ALTER SERVICE {db}.AGENT.STRATA_SERVICE FROM SPECIFICATION $${spec}$$", connection)
    else:
        snow_sql(f"CREATE SERVICE {db}.AGENT.STRATA_SERVICE IN COMPUTE POOL SCM_POOL_{env.upper()} "
                 f"FROM SPECIFICATION $${spec}$$ QUERY_WAREHOUSE = SCM_WH_{env.upper()}", connection)
    # Without the service role the ingress cannot resolve the endpoint for a user, and the token
    # exchange answers 395042 rather than a privilege error.
    for role in ENDPOINT_ROLES:
        snow_sql(f"GRANT SERVICE ROLE {db}.AGENT.STRATA_SERVICE!ALL_ENDPOINTS_USAGE TO ROLE {role}", connection)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["deploy", "rollback"])
    p.add_argument("--env", default="dev", choices=["dev", "test", "prod"])
    p.add_argument("--connection", required=True)
    p.add_argument("--tag")
    a = p.parse_args()
    db = f"SCM_{a.env.upper()}"
    if a.action == "deploy":
        if not a.tag or not a.tag.isalnum():
            raise SystemExit("--tag must be a short git sha")
        apply(a.env, a.tag, a.connection)
        snow_sql(f"INSERT INTO {db}.OPS.IMAGE_VERSIONS (tag) SELECT '{a.tag}'", a.connection)
    else:
        rows = snow_sql(f"SELECT tag FROM {db}.OPS.IMAGE_VERSIONS ORDER BY deployed_at DESC LIMIT 2",
                        a.connection).splitlines()[1:]
        if len(rows) < 2:
            raise SystemExit("no previous image recorded")
        apply(a.env, rows[1].strip(), a.connection)
    return 0


if __name__ == "__main__":
    sys.exit(main())
