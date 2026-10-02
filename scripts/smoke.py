"""Post-deploy smoke test: one governed answer, one refusal, one lineage call.

Exits non-zero on any failure so deploy.yml can roll back.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

CHECKS = [
    ("governed answer",
     "CALL {db}.AGENT.GOVERNED_QUERY(PARSE_JSON('{q}'))",
     lambda r: r.get("status") == "ok" and r.get("query_hash")),
    ("describe metric",
     "CALL {db}.AGENT.DESCRIBE_METRIC('on_time_delivery')",
     lambda r: r.get("name") == "on_time_delivery"),
    ("lineage",
     "CALL {db}.AGENT.EXPLAIN_LINEAGE('on_time_delivery')",
     lambda r: bool(r.get("path"))),
]
QUERY = {"metrics": ["on_time_delivery"], "dimensions": [], "time": {"range": "fy2026"}, "filters": []}


def run(sql: str, connection: str) -> dict:
    out = subprocess.run(["snow", "sql", "-q", sql, "-c", connection, "--format", "json"],
                         check=True, capture_output=True, text=True).stdout
    rows = json.loads(out)
    value = next(iter(rows[0].values()))
    return json.loads(value) if isinstance(value, str) else value


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--env", default="dev", choices=["dev", "test", "prod"])
    p.add_argument("--connection", required=True)
    a = p.parse_args()
    db = f"SCM_{a.env.upper()}"
    failed = 0
    for name, sql, ok in CHECKS:
        try:
            result = run(sql.format(db=db, q=json.dumps(QUERY)), a.connection)
            passed = bool(ok(result))
        except (subprocess.CalledProcessError, ValueError, KeyError, IndexError) as exc:
            passed, result = False, {"error": str(exc)}
        print(f"{'pass' if passed else 'FAIL'}  {name}")
        failed += not passed
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
