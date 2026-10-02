from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
WAREHOUSE = ROOT / "dbt" / "target" / "scm.duckdb"


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    if not WAREHOUSE.exists():
        pytest.skip("run `make data dbt-local` first; the DuckDB build is missing")
    os.environ["SCM_BACKEND"] = "local"
    os.environ["SCM_STATE_DIR"] = str(tmp_path_factory.mktemp("strata_state"))
    os.environ["SCM_RATE_PER_MINUTE"] = "1000"
    from api import backend
    from api.main import app

    backend.set_backend(None)
    with TestClient(app) as test_client:
        yield test_client
    backend.set_backend(None)
