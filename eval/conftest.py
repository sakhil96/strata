from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import duckdb
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ontology"))
import semantic  # noqa: E402

TRUTH = ROOT / "data" / "out" / "truth_metrics.parquet"
WAREHOUSE = ROOT / "dbt" / "target" / "scm.duckdb"


def _stale() -> bool:
    return not WAREHOUSE.exists() or WAREHOUSE.stat().st_mtime < TRUTH.stat().st_mtime


@pytest.fixture(scope="session")
def registry() -> semantic.Registry:
    return semantic.load_registry()


@pytest.fixture(scope="session")
def truth() -> pd.DataFrame:
    if not TRUTH.exists():
        pytest.skip("run `make data` first; truth_metrics.parquet is missing")
    return pd.read_parquet(TRUTH)


@pytest.fixture(scope="session")
def warehouse(truth: pd.DataFrame):
    if _stale():
        env = {**os.environ, "SCM_DUCKDB": str(WAREHOUSE)}
        subprocess.run(["dbt", "build", "--profiles-dir", ".", "--target", "local", "--quiet"],
                       cwd=ROOT / "dbt", check=True, env=env)
    connection = duckdb.connect(str(WAREHOUSE), read_only=True)
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def account():
    """A cursor on the deployed environment. Skips with 'needs account' when the run is local."""
    if os.getenv("SCM_BACKEND") != "snowflake":
        pytest.skip("needs account: set SCM_BACKEND=snowflake and SNOWFLAKE_CONNECTION_NAME")
    import snowflake.connector

    env = os.getenv("SCM_ENV", "dev")
    conn = snowflake.connector.connect(connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME", f"scm_{env}"),
                                       database=f"SCM_{env.upper()}")
    yield conn.cursor(), f"SCM_{env.upper()}"
    conn.close()
