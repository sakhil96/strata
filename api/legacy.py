"""The three on-time-delivery numbers the business reported before the ontology.

Each runs on RAW, the way the team that owned it computed it. They exist so /before-after
can show why the numbers disagreed; nothing else may use them.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

TABLES = ("sales_order_lines", "shipment_lines", "shipments", "storage_locations")
SYSTEM = {"sales_order_lines": "erp", "storage_locations": "erp", "shipment_lines": "tms", "shipments": "tms"}

DEFINITIONS = [
    {
        "key": "planning_requested_date",
        "team": "Planning",
        "label": "Planning workbook",
        "basis": "Proof of delivery on or before the customer's requested date; cancelled lines dropped.",
        "sql": """
            SELECT SUM(CASE WHEN s.pod_date <= l.req_dlv_date THEN 1 ELSE 0 END) * 1.0 / COUNT(*)
            FROM {sales_order_lines} l
            JOIN {shipment_lines} sl ON sl.vbeln = l.vbeln AND sl.posnr = l.posnr AND sl.leg = 1
            JOIN {shipments} s ON s.shipment_no = sl.shipment_no
            WHERE l.abgru = '' AND s.pod_date BETWEEN '{start}' AND '{end}'
        """,
    },
    {
        "key": "logistics_carrier_eta",
        "team": "Logistics",
        "label": "Carrier scorecard",
        "basis": "Shipments delivered on or before the carrier's ETA, counted per shipment, not per line.",
        "sql": """
            SELECT SUM(CASE WHEN s.pod_date <= s.carrier_eta THEN 1 ELSE 0 END) * 1.0 / COUNT(*)
            FROM {shipments} s
            WHERE s.pod_date BETWEEN '{start}' AND '{end}'
        """,
    },
    {
        "key": "executive_plant_average",
        "team": "Executive",
        "label": "Board dashboard",
        "basis": "Committed date, cancelled lines left in the denominator, then the five plant rates averaged.",
        "sql": """
            SELECT AVG(plant_rate) FROM (
                SELECT loc.plant_id,
                       SUM(CASE WHEN l.abgru = '' AND s.pod_date <= l.conf_dlv_date THEN 1 ELSE 0 END) * 1.0
                           / COUNT(*) AS plant_rate
                FROM {sales_order_lines} l
                JOIN {storage_locations} loc ON loc.storage_location_id = l.lgort
                LEFT JOIN {shipment_lines} sl ON sl.vbeln = l.vbeln AND sl.posnr = l.posnr AND sl.leg = 1
                LEFT JOIN {shipments} s ON s.shipment_no = sl.shipment_no
                WHERE COALESCE(s.pod_date, l.conf_dlv_date) BETWEEN '{start}' AND '{end}'
                GROUP BY loc.plant_id
            ) per_plant
        """,
    },
]


def local_sources(data_dir: Path) -> dict[str, str]:
    return {t: f"read_parquet('{(data_dir / SYSTEM[t] / f'{t}.parquet').as_posix()}')" for t in TABLES}


def snowflake_sources(database: str) -> dict[str, str]:
    return {t: f"{database}.RAW.{t.upper()}" for t in TABLES}


def run(cursor: Any, sources: dict[str, str], start: date, end_month: date) -> list[dict[str, Any]]:
    end = date(end_month.year + (end_month.month == 12), end_month.month % 12 + 1, 1)
    out = []
    for d in DEFINITIONS:
        sql = d["sql"].format(**sources, start=start.isoformat(), end=(end.fromordinal(end.toordinal() - 1)).isoformat())
        value = cursor.execute(sql).fetchone()[0]
        out.append({k: d[k] for k in ("key", "team", "label", "basis")} | {"value": float(value)})
    return out
