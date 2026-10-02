"""Load generated Parquet data into Snowflake RAW schema.

Stages files with `snow stage copy`, runs COPY INTO for each table, and records
a load log (file, rows, checksum, loaded_at) so every load is auditable and
re-runnable. Also loads reference data and truth metrics.
"""

from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path

import click

DATA_DIR = Path(__file__).resolve().parent / "out"

LOAD_MAP = {
    "erp/suppliers.parquet": "SUPPLIERS",
    "erp/parts.parquet": "PARTS",
    "erp/agreements.parquet": "SUPPLIER_PART_AGREEMENTS",
    "erp/purchase_orders.parquet": "PURCHASE_ORDER_LINES",
    "erp/goods_receipts.parquet": "GOODS_RECEIPTS",
    "erp/sales_orders.parquet": "SALES_ORDER_LINES",
    "erp/inventory_snapshots.parquet": "INVENTORY_SNAPSHOTS",
    "erp/customers.parquet": "CUSTOMERS",
    "erp/storage_locations.parquet": "STORAGE_LOCATIONS",
    "tms/shipments.parquet": "SHIPMENTS",
    "tms/shipment_lines.parquet": "SHIPMENT_LINES",
    "tms/carriers.parquet": "CARRIERS",
    "tms/lanes.parquet": "LANES",
    "portal/delivery_events.parquet": "DELIVERY_EVENTS",
    "iot/tariff_codes.parquet": "TARIFF_CODES",
    "iot/fx_rates.parquet": "FX_RATES",
}

TRUTH_MAP = {
    "truth_metrics.parquet": "TRUTH_METRICS",
}

REFERENCE_MAP = {
    "reference/hts_2026.csv": "HTS_2026",
    "reference/gscpi.csv": "GSCPI",
}


def file_checksum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


@click.command()
@click.option("--env", default="dev", type=click.Choice(["dev", "test", "prod"]))
@click.option("--dry-run", is_flag=True, help="Print commands without executing")
def load_data(env: str, dry_run: bool) -> None:
    """Load generated data into Snowflake."""
    db = f"SCM_{env.upper()}"

    click.echo(f"Loading data into {db}")

    # Create load log table if not exists
    create_log_sql = f"""
    CREATE TABLE IF NOT EXISTS {db}.OPS.LOAD_LOG (
        file_name STRING,
        table_name STRING,
        row_count INTEGER,
        checksum STRING,
        loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
    );
    """
    run_sql(create_log_sql, dry_run)

    # Create freshness table
    create_freshness_sql = f"""
    CREATE TABLE IF NOT EXISTS {db}.OPS.FRESHNESS (
        source_system STRING,
        table_name STRING,
        last_loaded_at TIMESTAMP_NTZ,
        row_count INTEGER
    );
    """
    run_sql(create_freshness_sql, dry_run)

    # Load source data into RAW
    for rel_path, table_name in LOAD_MAP.items():
        file_path = DATA_DIR / rel_path
        if not file_path.exists():
            click.echo(f"  skipping {rel_path} (not found)")
            continue

        checksum = file_checksum(file_path)
        stage_path = f"@{db}.RAW.SOURCE_DATA/{rel_path}"

        click.echo(f"  staging {rel_path} -> {stage_path}")
        run_cmd(f"snow stage copy {file_path} {stage_path} --overwrite", dry_run)

        click.echo(f"  loading {table_name}")
        copy_sql = f"""
        CREATE TABLE IF NOT EXISTS {db}.RAW.{table_name}
            USING TEMPLATE (
                SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                FROM TABLE(INFER_SCHEMA(
                    LOCATION => '{stage_path}',
                    FILE_FORMAT => 'PARQUET'
                ))
            );
        COPY INTO {db}.RAW.{table_name}
            FROM {stage_path}
            FILE_FORMAT = (TYPE = PARQUET)
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
        """
        run_sql(copy_sql, dry_run)

        # Log the load
        log_sql = f"""
        INSERT INTO {db}.OPS.LOAD_LOG (file_name, table_name, row_count, checksum)
        SELECT '{rel_path}', '{table_name}', COUNT(*), '{checksum}'
        FROM {db}.RAW.{table_name};
        """
        run_sql(log_sql, dry_run)

        # Update freshness
        source = rel_path.split("/")[0]
        freshness_sql = f"""
        MERGE INTO {db}.OPS.FRESHNESS t
        USING (SELECT '{source}' AS source_system, '{table_name}' AS table_name,
               CURRENT_TIMESTAMP() AS last_loaded_at,
               (SELECT COUNT(*) FROM {db}.RAW.{table_name}) AS row_count) s
        ON t.source_system = s.source_system AND t.table_name = s.table_name
        WHEN MATCHED THEN UPDATE SET last_loaded_at = s.last_loaded_at, row_count = s.row_count
        WHEN NOT MATCHED THEN INSERT VALUES (s.source_system, s.table_name, s.last_loaded_at, s.row_count);
        """
        run_sql(freshness_sql, dry_run)

    # Load truth metrics into EVAL
    for rel_path, table_name in TRUTH_MAP.items():
        file_path = DATA_DIR / rel_path
        if not file_path.exists():
            continue

        stage_path = f"@{db}.EVAL.TRUTH_STAGE/{rel_path}"
        run_cmd(f"snow stage copy {file_path} {stage_path} --overwrite", dry_run)

        copy_sql = f"""
        CREATE TABLE IF NOT EXISTS {db}.EVAL.{table_name}
            USING TEMPLATE (
                SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
                FROM TABLE(INFER_SCHEMA(
                    LOCATION => '{stage_path}',
                    FILE_FORMAT => 'PARQUET'
                ))
            );
        COPY INTO {db}.EVAL.{table_name}
            FROM {stage_path}
            FILE_FORMAT = (TYPE = PARQUET)
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
        """
        run_sql(copy_sql, dry_run)

    click.echo("Load complete.")


def run_sql(sql: str, dry_run: bool) -> None:
    if dry_run:
        click.echo(f"    [dry-run] {sql.strip()[:120]}...")
    else:
        os.system(f'snow sql -q "{sql.strip()}"')


def run_cmd(cmd: str, dry_run: bool) -> None:
    if dry_run:
        click.echo(f"    [dry-run] {cmd}")
    else:
        os.system(cmd)


if __name__ == "__main__":
    load_data()
