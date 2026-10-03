"""Build the Snowflake-hosted copy of dbt/ in .strata/dbt_snowflake.

dbt Projects on Snowflake authenticate with the session, so the copy's profiles.yml carries no
credentials, and every env_var() must be DBT_-prefixed and backed by env.yml. dbt/ itself stays
as it is for the local DuckDB build and for laptops running dbt against Snowflake.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "dbt"
COPY = ROOT / ".strata" / "dbt_snowflake"


def main() -> int:
    shutil.rmtree(COPY, ignore_errors=True)
    shutil.copytree(SOURCE, COPY, ignore=shutil.ignore_patterns("target", "logs", "dbt_packages", "*.duckdb"))
    outputs = {}
    for env in ("dev", "test", "prod"):
        settings = yaml.safe_load((ROOT / "snowflake" / "environments" / f"{env}.yaml").read_text())
        outputs[env] = {
            "type": "snowflake", "account": "not needed", "user": "not needed",
            "role": "SCM_DEPLOY", "warehouse": settings["warehouse"], "database": settings["database"],
            "schema": "STAGING", "threads": 4,
        }
    (COPY / "profiles.yml").write_text(yaml.safe_dump({"scm_ontology": {"target": "dev", "outputs": outputs}},
                                                      sort_keys=False))
    # external_location is a DuckDB-only hint; on Snowflake the sources are RAW tables.
    (COPY / "env.yml").write_text(yaml.safe_dump({"env_config": {
        "default_environment": "dev",
        "environments": [{"name": env, "env": {"DBT_SCM_DATA_DIR": "unused-on-snowflake"}} for env in ("dev", "test", "prod")],
    }}, sort_keys=False))
    sources = COPY / "models" / "staging" / "sources.yml"
    sources.write_text(sources.read_text().replace("env_var('SCM_DATA_DIR'", "env_var('DBT_SCM_DATA_DIR'"))
    left = [p for p in COPY.rglob("*") if p.is_file() and p.suffix in {".yml", ".sql"}
            and "env_var('SCM_" in p.read_text()]
    if left:
        raise SystemExit(f"unprefixed env_var left in {left}")
    print(f"wrote {COPY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
