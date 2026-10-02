"""Load the simulated source systems into RAW, with a load log and freshness per source.

Each file is PUT to the RAW stage, its table is created from the file's own schema, and it is
copied in with a checksum recorded in OPS.LOAD_LOG. Running it twice reloads the same rows:
tables are truncated before the copy, and the log keeps every attempt.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import click

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
SYSTEMS = ("erp", "tms", "portal", "iot", "content")


@dataclass(frozen=True)
class Load:
    system: str
    path: Path
    table: str
    checksum: str


def plan(out: Path = OUT) -> list[Load]:
    loads = []
    for system in SYSTEMS:
        for path in sorted((out / system).glob("*.parquet")):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            loads.append(Load(system, path, path.stem.upper(), digest))
    truth = out / "truth_metrics.parquet"
    if truth.exists():
        loads.append(Load("eval", truth, "TRUTH_METRICS", hashlib.sha256(truth.read_bytes()).hexdigest()))
    return loads


def statements(load: Load, db: str) -> list[tuple[str, tuple]]:
    schema = "EVAL" if load.system == "eval" else "RAW"
    stage = f"@{db}.RAW.SOURCE_DATA/{load.system}"
    table = f"{db}.{schema}.{load.table}"
    location = f"{stage}/{load.path.name}"
    return [
        (f"PUT 'file://{load.path.as_posix()}' {stage} AUTO_COMPRESS = FALSE OVERWRITE = TRUE", ()),
        (f"CREATE TABLE IF NOT EXISTS {table} USING TEMPLATE (SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*)) "
         f"FROM TABLE(INFER_SCHEMA(LOCATION => '{location}', FILE_FORMAT => '{db}.RAW.PARQUET_FILES')))", ()),
        (f"TRUNCATE TABLE {table}", ()),
        (f"COPY INTO {table} FROM {location} FILE_FORMAT = (FORMAT_NAME = '{db}.RAW.PARQUET_FILES') "
         "MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE ON_ERROR = ABORT_STATEMENT", ()),
        (f"INSERT INTO {db}.OPS.LOAD_LOG (file_name, table_name, row_count, checksum) "
         f"SELECT %s, %s, COUNT(*), %s FROM {table}", (f"{load.system}/{load.path.name}", load.table, load.checksum)),
        (f"MERGE INTO {db}.OPS.FRESHNESS f USING (SELECT %s AS source_system, %s AS table_name, "
         f"CURRENT_TIMESTAMP() AS last_loaded_at, (SELECT COUNT(*) FROM {table}) AS row_count) s "
         "ON f.source_system = s.source_system AND f.table_name = s.table_name "
         "WHEN MATCHED THEN UPDATE SET last_loaded_at = s.last_loaded_at, row_count = s.row_count "
         "WHEN NOT MATCHED THEN INSERT VALUES (s.source_system, s.table_name, s.last_loaded_at, s.row_count)",
         (load.system, load.table)),
    ]


@click.command()
@click.option("--env", default="dev", type=click.Choice(["dev", "test", "prod"]))
@click.option("--connection", default=None, help="Connection name in connections.toml; defaults to scm_<env>.")
@click.option("--dry-run", is_flag=True, help="Print the statements without connecting.")
def main(env: str, connection: str | None, dry_run: bool) -> None:
    db = f"SCM_{env.upper()}"
    loads = plan()
    if not loads:
        raise click.ClickException("nothing to load; run `make data` first")
    setup = [(f"CREATE FILE FORMAT IF NOT EXISTS {db}.RAW.PARQUET_FILES TYPE = PARQUET", ())]
    if dry_run:
        for sql, params in setup + [s for load in loads for s in statements(load, db)]:
            click.echo(f"{sql};" + (f"  -- {params}" if params else ""))
        return
    import snowflake.connector

    with snowflake.connector.connect(connection_name=connection or f"scm_{env}", database=db) as conn:
        cur = conn.cursor()
        for sql, params in setup:
            cur.execute(sql, params)
        for load in loads:
            for sql, params in statements(load, db):
                cur.execute(sql, params)
            click.echo(f"  {load.system}/{load.path.name} -> {load.table}")
    click.echo(f"loaded {len(loads)} files into {db}")


if __name__ == "__main__":
    sys.exit(main())
