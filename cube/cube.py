"""Cube.py — local DuckDB + Cube fallback for development and CI.

Loads generated Parquet into DuckDB and starts a Cube dev server
that exposes the same metrics as the Snowflake semantic views.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import duckdb

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "out"
DB_PATH = Path(__file__).resolve().parent / "scm.duckdb"


def create_duckdb():
    conn = duckdb.connect(str(DB_PATH))
    parquet_files = list(DATA_DIR.rglob("*.parquet"))
    for pf in parquet_files:
        table_name = pf.stem
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{pf}')")
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  loaded {table_name}: {count} rows")
    conn.close()
    print(f"DuckDB database: {DB_PATH}")


def main():
    print("Creating DuckDB from generated data...")
    create_duckdb()
    print("DuckDB ready. Start Cube with: npx cubejs-server")


if __name__ == "__main__":
    main()
