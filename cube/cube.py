"""Serve the local fallback: Cube over the same DuckDB build the API reads.

The cube and view files in cube/model come from compile.py; this writes the Cube config that
points them at dbt/target/scm.duckdb and starts Cube in development mode.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WAREHOUSE = ROOT / "dbt" / "target" / "scm.duckdb"


def main() -> int:
    if not WAREHOUSE.exists():
        print("The DuckDB build is missing; run `make data dbt-local` first.", file=sys.stderr)
        return 1
    if not shutil.which("npx"):
        print("Cube needs Node 22 and npx on the PATH.", file=sys.stderr)
        return 1
    env = {**os.environ, "CUBEJS_DB_TYPE": "duckdb", "CUBEJS_DB_DUCKDB_DATABASE_PATH": str(WAREHOUSE),
           "CUBEJS_DEV_MODE": "true", "CUBEJS_SCHEMA_PATH": "model", "CUBEJS_TELEMETRY": "false"}
    return subprocess.call(["npx", "--yes", "cubejs-server@1"], cwd=ROOT / "cube", env=env)


if __name__ == "__main__":
    sys.exit(main())
