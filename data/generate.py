"""Generate simulated supply chain data for the SCM Ontology project.

Creates four source systems (erp/, tms/, portal/, iot/) as Parquet files with
injected inconsistencies: three supplier key schemes, five date field names,
mixed UOMs, timezone variations, currency mixing, and duplicate supplier names.

Deterministic: seeded random state produces identical output on every run.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

SEED = 20261002
RNG = np.random.default_rng(SEED)
OUT_DIR = Path(__file__).resolve().parent / "out"

FISCAL_START = date(2025, 10, 1)
FISCAL_END = date(2026, 9, 30)
DAYS_IN_FY = (FISCAL_END - FISCAL_START).days + 1

PLANTS = [
    {"plant_id": "PLT-US01", "name": "Chicago Manufacturing", "type": "MANUFACTURING", "region": "US", "country": "US", "tz": "America/Chicago"},
    {"plant_id": "PLT-DE01", "name": "Stuttgart Manufacturing", "type": "MANUFACTURING", "region": "EMEA", "country": "DE", "tz": "Europe/Berlin"},
    {"plant_id": "PLT-SG01", "name": "Singapore Manufacturing", "type": "MANUFACTURING", "region": "APAC", "country": "SG", "tz": "Asia/Singapore"},
    {"plant_id": "DC-US01", "name": "Atlanta Distribution Center", "type": "DISTRIBUTION", "region": "US", "country": "US", "tz": "America/New_York"},
    {"plant_id": "DC-DE01", "name": "Rotterdam Distribution Center", "type": "DISTRIBUTION", "region": "EMEA", "country": "NL", "tz": "Europe/Amsterdam"},
]

STORAGE_TYPES = ["RACK", "BULK", "COLD", "YARD"]

SEGMENTS = ["Industrial", "Retail", "Government", "Healthcare"]

CATEGORIES = ["Electronics", "Mechanical", "Chemical", "Packaging", "Raw Material", "Consumable"]
FAMILIES_PER_CATEGORY = 3

CARRIER_TYPES = ["OCEAN", "AIR", "ROAD", "RAIL", "PARCEL"]

INCOTERMS = ["EXW", "FOB", "CIF", "DDP"]
CURRENCIES = ["USD", "EUR", "SGD"]

EVENT_TYPES = ["picked_up", "departed", "arrived", "delivered", "exception"]

COUNTRIES_8 = ["US", "DE", "CN", "JP", "KR", "MX", "IN", "GB"]


def gen_id(prefix: str, n: int) -> str:
    return f"{prefix}-{n:04d}"


def random_date_in_range(start: date, end: date, size: int = 1) -> list[date]:
    days = (end - start).days
    offsets = RNG.integers(0, days, size=size)
    return [start + timedelta(days=int(d)) for d in offsets]


def generate_suppliers(n: int = 40) -> pd.DataFrame:
    rows = []
    for i in range(n):
        country = COUNTRIES_8[i % len(COUNTRIES_8)]
        currency = {"US": "USD", "DE": "EUR", "GB": "EUR", "CN": "USD", "JP": "USD",
                     "KR": "USD", "MX": "USD", "IN": "USD", "SG": "SGD"}.get(country, "USD")

        # Three supplier key schemes (injected inconsistency)
        if i % 3 == 0:
            sid = f"SUP{i + 1:04d}"
        elif i % 3 == 1:
            sid = f"V-{i + 1:06d}"
        else:
            sid = f"VENDOR_{i + 1}"

        name = f"{'Global' if i < 10 else 'Regional'} {'Components' if i % 4 == 0 else 'Materials' if i % 4 == 1 else 'Assemblies' if i % 4 == 2 else 'Parts'} {'Inc' if country == 'US' else 'GmbH' if country == 'DE' else 'Ltd' if country in ('GB', 'IN', 'SG') else 'Co'} {chr(65 + i % 26)}"

        # Duplicate name variant (injected inconsistency)
        if i > 0 and i % 10 == 0:
            name = rows[i - 1]["supplier_name"] + " (subsidiary)"

        rows.append({
            "supplier_id": sid,
            "supplier_name": name,
            "supplier_site": f"SITE-{country}-{i % 3 + 1}",
            "parent_supplier_id": rows[max(0, i - (i % 5))]["supplier_id"] if i >= 5 else None,
            "country_code": country,
            "contact_name": f"Contact Person {i + 1}",
            "contact_email": f"contact{i + 1}@supplier{i + 1}.example.com",
            "bank_account": f"BANK{RNG.integers(10000000, 99999999)}",
            "currency": currency,
        })
    return pd.DataFrame(rows)


def generate_parts(n: int = 300) -> pd.DataFrame:
    rows = []
    families = []
    for cat in CATEGORIES:
        for j in range(FAMILIES_PER_CATEGORY):
            families.append({"category": cat, "family": f"{cat[:4]}-Family-{j + 1}"})

    for i in range(n):
        fam = families[i % len(families)]
        uom_choice = RNG.choice(["each", "kg", "litre"])
        rows.append({
            "part_id": gen_id("PRT", i + 1),
            "part_name": f"{fam['family']} Part {i + 1}",
            "part_family": fam["family"],
            "category": fam["category"],
            "base_uom": uom_choice,
            "pack_factor": float(RNG.choice([1, 6, 12, 24])),
            "pallet_factor": float(RNG.choice([10, 20, 40])),
            "weight_kg": round(float(RNG.uniform(0.1, 50.0)), 2),
        })
    return pd.DataFrame(rows)


def generate_customers(n: int = 120) -> pd.DataFrame:
    rows = []
    for i in range(n):
        segment = SEGMENTS[i % len(SEGMENTS)]
        country = RNG.choice(["US", "DE", "GB", "SG", "JP", "AU"])
        rows.append({
            "customer_id": gen_id("CUST", i + 1),
            "customer_name": f"{segment} Customer {i + 1}",
            "ship_to_id": gen_id("SHIP", i + 1),
            "sold_to_id": gen_id("SOLD", (i // 3) + 1),
            "account_id": gen_id("ACCT", (i // 6) + 1),
            "segment": segment,
            "country_code": country,
            "contact_name": f"Buyer {i + 1}",
            "contact_email": f"buyer{i + 1}@customer{i + 1}.example.com",
        })
    return pd.DataFrame(rows)


def generate_carriers(n: int = 12) -> pd.DataFrame:
    rows = []
    for i in range(n):
        ctype = CARRIER_TYPES[i % len(CARRIER_TYPES)]
        rows.append({
            "carrier_id": gen_id("CAR", i + 1),
            "carrier_name": f"{'Pacific' if i < 4 else 'Atlantic' if i < 8 else 'Express'} {ctype.title()} Lines {chr(65 + i)}",
            "carrier_type": ctype,
            "scac_code": f"SC{chr(65 + i)}{chr(65 + (i * 3) % 26)}",
        })
    return pd.DataFrame(rows)


def generate_lanes(carriers: pd.DataFrame) -> pd.DataFrame:
    regions = ["US", "EMEA", "APAC"]
    rows = []
    lane_id = 0
    for orig in regions:
        for dest in regions:
            lane_id += 1
            mode = "OCEAN" if orig != dest else "ROAD"
            transit = 3 if orig == dest else (14 if mode == "OCEAN" else 7)
            rows.append({
                "lane_id": gen_id("LANE", lane_id),
                "origin_region": orig,
                "destination_region": dest,
                "mode": mode,
                "transit_days_typical": transit,
            })
    return pd.DataFrame(rows)


def generate_tariff_codes(parts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    tariff_id = 0
    # Assign tariff codes to parts — some parts share codes
    hts_codes = [f"8501.{10 + i:02d}.{j:02d}00" for i in range(20) for j in range(3)]
    for i, part_row in parts.iterrows():
        hts = hts_codes[i % len(hts_codes)]
        base_rate = round(float(RNG.uniform(0.0, 0.15)), 4)

        # Pre-step rate
        tariff_id += 1
        rows.append({
            "tariff_id": gen_id("TAR", tariff_id),
            "hts_code": hts,
            "description": f"Tariff for {part_row['part_name'][:30]}",
            "duty_rate": base_rate,
            "effective_from": str(FISCAL_START),
            "effective_to": "2026-07-23",
            "part_id": part_row["part_id"],
        })

        # Post-step rate (2026-07-24 tariff increase)
        tariff_id += 1
        rows.append({
            "tariff_id": gen_id("TAR", tariff_id),
            "hts_code": hts,
            "description": f"Tariff for {part_row['part_name'][:30]} (post-step)",
            "duty_rate": round(base_rate + float(RNG.uniform(0.02, 0.08)), 4),
            "effective_from": "2026-07-24",
            "effective_to": str(FISCAL_END),
            "part_id": part_row["part_id"],
        })
    return pd.DataFrame(rows)


def generate_fx_rates() -> pd.DataFrame:
    rows = []
    current = FISCAL_START
    eur_rate = 1.08
    sgd_rate = 0.74
    while current <= FISCAL_END:
        eur_rate += float(RNG.normal(0, 0.002))
        sgd_rate += float(RNG.normal(0, 0.001))
        eur_rate = max(0.9, min(1.3, eur_rate))
        sgd_rate = max(0.6, min(0.9, sgd_rate))

        rows.append({"fx_date": str(current), "from_currency": "EUR", "to_currency": "USD", "rate": round(eur_rate, 6)})
        rows.append({"fx_date": str(current), "from_currency": "SGD", "to_currency": "USD", "rate": round(sgd_rate, 6)})
        rows.append({"fx_date": str(current), "from_currency": "USD", "to_currency": "USD", "rate": 1.0})
        current += timedelta(days=1)
    return pd.DataFrame(rows)


def generate_storage_locations(plants: list[dict]) -> pd.DataFrame:
    rows = []
    loc_id = 0
    for plant in plants:
        for stype in STORAGE_TYPES[:3]:
            loc_id += 1
            rows.append({
                "storage_location_id": gen_id("LOC", loc_id),
                "storage_location_name": f"{plant['name']} {stype}",
                "plant_id": plant["plant_id"],
                "location_type": stype,
            })
    return pd.DataFrame(rows)


def generate_agreements(suppliers: pd.DataFrame, parts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    agr_id = 0
    for i in range(len(suppliers)):
        n_parts = RNG.integers(5, 20)
        part_indices = RNG.choice(len(parts), size=min(n_parts, len(parts)), replace=False)
        for pi in part_indices:
            agr_id += 1
            currency = suppliers.iloc[i]["currency"]
            rows.append({
                "agreement_id": gen_id("AGR", agr_id),
                "supplier_id": suppliers.iloc[i]["supplier_id"],
                "part_id": parts.iloc[pi]["part_id"],
                "unit_cost": round(float(RNG.uniform(1.0, 500.0)), 2),
                "currency": currency,
                "incoterm": RNG.choice(INCOTERMS),
                "quoted_lead_days": int(RNG.integers(7, 60)),
                "effective_from": str(FISCAL_START),
                "effective_to": str(FISCAL_END),
            })
    return pd.DataFrame(rows)


def generate_purchase_orders(
    suppliers: pd.DataFrame,
    parts: pd.DataFrame,
    agreements: pd.DataFrame,
    n: int = 8000,
) -> pd.DataFrame:
    rows = []
    for i in range(n):
        agr_idx = RNG.integers(0, len(agreements))
        agr = agreements.iloc[agr_idx]
        order_date = random_date_in_range(FISCAL_START, FISCAL_END - timedelta(days=30))[0]
        lead = int(RNG.integers(7, 45))
        promised = order_date + timedelta(days=lead)
        confirmed = promised + timedelta(days=int(RNG.integers(-3, 5)))

        # Some cancelled
        is_cancelled = RNG.random() < 0.03
        status = "CANCELLED" if is_cancelled else "OPEN"

        # Five differently named date fields (injected inconsistency)
        date_field_name = RNG.choice(["promised_date", "promise_dt", "prom_date", "supplier_promise", "eta_date"])

        qty = float(RNG.integers(10, 500))
        plant_idx = RNG.integers(0, len(PLANTS))

        rows.append({
            "po_line_id": gen_id("POL", i + 1),
            "po_number": f"PO-{(i // 3) + 1:06d}",
            "line_number": (i % 3) + 1,
            "supplier_id": agr["supplier_id"],
            "part_id": agr["part_id"],
            "deliver_to_plant_id": PLANTS[plant_idx]["plant_id"],
            "ordered_qty": qty,
            "unit_cost": agr["unit_cost"],
            "currency": agr["currency"],
            "order_date": str(order_date),
            "promised_date": str(promised),
            "confirmed_date": str(confirmed),
            "status": status,
            # UOM inconsistency
            "uom": RNG.choice(["EA", "each", "EACH", "CS", "case"]),
            # Extra field with alternative name
            f"_{date_field_name}": str(promised),
        })
    return pd.DataFrame(rows)


def generate_receipts(po_lines: pd.DataFrame) -> pd.DataFrame:
    rows = []
    receipt_id = 0
    for _, po in po_lines.iterrows():
        if po["status"] == "CANCELLED":
            continue
        receipt_id += 1
        promised = datetime.strptime(po["promised_date"], "%Y-%m-%d").date()
        # Receipt date: most on time, some early, some late
        offset = int(RNG.normal(0, 3))
        receipt_date = promised + timedelta(days=offset)
        receipt_date = max(receipt_date, datetime.strptime(po["order_date"], "%Y-%m-%d").date() + timedelta(days=3))

        received_qty = po["ordered_qty"]
        # Some partial receipts
        if RNG.random() < 0.08:
            received_qty = round(received_qty * float(RNG.uniform(0.5, 0.95)), 0)
            status = "PARTIAL"
        else:
            status = "RECEIVED"

        rows.append({
            "receipt_id": gen_id("RCV", receipt_id),
            "po_line_id": po["po_line_id"],
            "receipt_date": str(receipt_date),
            "received_qty": float(received_qty),
            "quality_status": RNG.choice(["ACCEPTED", "ACCEPTED", "ACCEPTED", "QUARANTINE", "REJECTED"]),
            "inspector_name": f"Inspector {RNG.integers(1, 20)}",
        })

        # Update PO status
        po_lines.loc[po_lines["po_line_id"] == po["po_line_id"], "status"] = status

    return pd.DataFrame(rows)


def generate_sales_orders(
    customers: pd.DataFrame,
    parts: pd.DataFrame,
    storage_locs: pd.DataFrame,
    n: int = 60000,
) -> pd.DataFrame:
    rows = []
    for i in range(n):
        cust_idx = RNG.integers(0, len(customers))
        part_idx = RNG.integers(0, len(parts))
        loc_idx = RNG.integers(0, len(storage_locs))

        order_date = random_date_in_range(FISCAL_START, FISCAL_END - timedelta(days=14))[0]
        requested = order_date + timedelta(days=int(RNG.integers(3, 21)))
        committed = requested + timedelta(days=int(RNG.integers(-2, 3)))

        is_cancelled = RNG.random() < 0.04
        qty = float(RNG.integers(1, 200))

        if is_cancelled:
            status = "CANCELLED"
            actual_ship = None
            actual_delivery = None
        else:
            ship_offset = int(RNG.normal(-1, 2))
            actual_ship_date = committed + timedelta(days=ship_offset)
            delivery_offset = int(RNG.integers(1, 8))
            actual_delivery_date = actual_ship_date + timedelta(days=delivery_offset)
            actual_ship = str(actual_ship_date)
            actual_delivery = str(actual_delivery_date)
            status = "DELIVERED" if actual_delivery_date <= FISCAL_END else "SHIPPED"

        rows.append({
            "so_line_id": gen_id("SOL", i + 1),
            "so_number": f"SO-{(i // 4) + 1:06d}",
            "line_number": (i % 4) + 1,
            "customer_id": customers.iloc[cust_idx]["customer_id"],
            "part_id": parts.iloc[part_idx]["part_id"],
            "fulfilled_from_location_id": storage_locs.iloc[loc_idx]["storage_location_id"],
            "ordered_qty": qty,
            "unit_price": round(float(RNG.uniform(5.0, 800.0)), 2),
            "currency": RNG.choice(CURRENCIES),
            "requested_date": str(requested),
            "committed_date": str(committed),
            "actual_ship_date": actual_ship,
            "actual_delivery_date": actual_delivery,
            "status": status,
            "order_date": str(order_date),
        })
    return pd.DataFrame(rows)


def generate_shipments_and_lines(
    so_lines: pd.DataFrame,
    carriers: pd.DataFrame,
    lanes: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    shipped_lines = so_lines[so_lines["status"].isin(["SHIPPED", "DELIVERED"])].copy()
    shipment_rows = []
    line_rows = []
    ship_id = 0

    # Group SO lines into shipments (3-5 lines per shipment)
    indices = list(shipped_lines.index)
    RNG.shuffle(indices)

    i = 0
    while i < len(indices):
        batch_size = min(int(RNG.integers(3, 6)), len(indices) - i)
        batch_indices = indices[i:i + batch_size]
        ship_id += 1

        carrier_idx = RNG.integers(0, len(carriers))
        lane_idx = RNG.integers(0, len(lanes))
        carrier = carriers.iloc[carrier_idx]
        lane = lanes.iloc[lane_idx]

        first_line = shipped_lines.loc[batch_indices[0]]
        ship_date_str = first_line["actual_ship_date"]
        if ship_date_str is None:
            i += batch_size
            continue

        ship_date = datetime.strptime(ship_date_str, "%Y-%m-%d").date()
        eta = ship_date + timedelta(days=lane["transit_days_typical"] + int(RNG.integers(-1, 3)))

        delivery_str = first_line["actual_delivery_date"]
        actual_del = datetime.strptime(delivery_str, "%Y-%m-%d").date() if delivery_str else eta

        total_weight = 0.0
        for idx in batch_indices:
            line = shipped_lines.loc[idx]
            weight = float(RNG.uniform(10, 500))
            total_weight += weight

        freight = round(float(RNG.uniform(200, 5000)), 2)

        shipment_rows.append({
            "shipment_id": gen_id("SHP", ship_id),
            "carrier_id": carrier["carrier_id"],
            "lane_id": lane["lane_id"],
            "origin_plant_id": PLANTS[RNG.integers(0, len(PLANTS))]["plant_id"],
            "destination_id": first_line["customer_id"],
            "ship_date": str(ship_date),
            "carrier_eta": str(eta),
            "actual_delivery": str(actual_del),
            "chargeable_weight_kg": round(total_weight, 2),
            "freight_charge": freight,
            "freight_currency": "USD",
            "status": "DELIVERED" if actual_del <= FISCAL_END else "IN_TRANSIT",
        })

        for j, idx in enumerate(batch_indices):
            line = shipped_lines.loc[idx]
            shipped_qty = line["ordered_qty"]
            # Some partial shipments
            is_partial = RNG.random() < 0.1
            if is_partial:
                shipped_qty = round(shipped_qty * float(RNG.uniform(0.6, 0.95)), 0)

            line_rows.append({
                "shipment_line_id": gen_id("SHL", len(line_rows) + 1),
                "shipment_id": gen_id("SHP", ship_id),
                "so_line_id": line["so_line_id"],
                "shipped_qty": float(shipped_qty),
                "is_first_shipment": j == 0 or not is_partial,
            })

        i += batch_size

    return pd.DataFrame(shipment_rows), pd.DataFrame(line_rows)


def generate_delivery_events(shipments: pd.DataFrame) -> pd.DataFrame:
    rows = []
    evt_id = 0
    for _, shp in shipments.iterrows():
        ship_date = datetime.strptime(shp["ship_date"], "%Y-%m-%d")
        delivery_date = datetime.strptime(shp["actual_delivery"], "%Y-%m-%d")
        n_events = int(RNG.integers(5, 9))
        total_hours = (delivery_date - ship_date).total_seconds() / 3600

        for j in range(n_events):
            evt_id += 1
            fraction = j / max(n_events - 1, 1)
            evt_time = ship_date + timedelta(hours=total_hours * fraction + float(RNG.normal(0, 2)))

            if j == 0:
                etype = "picked_up"
            elif j == n_events - 1:
                etype = "delivered"
            elif RNG.random() < 0.05:
                etype = "exception"
            elif j % 2 == 0:
                etype = "departed"
            else:
                etype = "arrived"

            # Timezone inconsistency: some events in site-local, some in UTC
            tz = RNG.choice(["UTC", "America/Chicago", "Europe/Berlin", "Asia/Singapore"])

            rows.append({
                "event_id": gen_id("EVT", evt_id),
                "shipment_id": shp["shipment_id"],
                "event_type": etype,
                "event_time_utc": evt_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "site_tz": tz,
                "location_id": f"LOC-{RNG.integers(1, 50):03d}",
            })

            # Late-arriving events (injected inconsistency): some delivered events arrive 2 days late
            if etype == "delivered" and RNG.random() < 0.15:
                evt_id += 1
                late_time = evt_time + timedelta(days=2)
                rows.append({
                    "event_id": gen_id("EVT", evt_id),
                    "shipment_id": shp["shipment_id"],
                    "event_type": "delivered",
                    "event_time_utc": late_time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "site_tz": tz,
                    "location_id": f"LOC-{RNG.integers(1, 50):03d}",
                })

    return pd.DataFrame(rows)


def generate_inventory_snapshots(
    storage_locs: pd.DataFrame,
    parts: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    snap_id = 0
    # Daily snapshots for a subset of location-part combinations
    n_combos = min(500, len(storage_locs) * len(parts))
    loc_indices = RNG.choice(len(storage_locs), size=n_combos, replace=True)
    part_indices = RNG.choice(len(parts), size=n_combos, replace=True)

    current = FISCAL_START
    while current <= FISCAL_END:
        for combo_idx in range(n_combos):
            snap_id += 1
            on_hand = max(0.0, float(RNG.normal(100, 40)))
            std_cost = round(float(RNG.uniform(5, 200)), 2)
            rows.append({
                "snapshot_id": gen_id("SNP", snap_id),
                "storage_location_id": storage_locs.iloc[loc_indices[combo_idx]]["storage_location_id"],
                "part_id": parts.iloc[part_indices[combo_idx]]["part_id"],
                "snapshot_date": str(current),
                "on_hand_qty": round(on_hand, 0),
                "on_hand_value_std": round(on_hand * std_cost, 2),
                "in_transit_qty": round(max(0.0, float(RNG.normal(20, 15))), 0),
                "allocated_qty": round(max(0.0, float(RNG.normal(30, 20))), 0),
            })
        current += timedelta(days=1)

    return pd.DataFrame(rows)


def compute_truth_metrics(
    so_lines: pd.DataFrame,
    shipment_lines: pd.DataFrame,
    po_lines: pd.DataFrame,
    receipts: pd.DataFrame,
    inventory: pd.DataFrame,
) -> pd.DataFrame:
    """Compute ground-truth values for all governed metrics by month x plant x region x segment x family."""
    # This is a simplified truth computation; the full version would join all tables
    # and compute exact metric values at every grouping level.
    truth_rows = []

    delivered = so_lines[so_lines["status"] == "DELIVERED"].copy()
    delivered["actual_delivery_date"] = pd.to_datetime(delivered["actual_delivery_date"])
    delivered["committed_date"] = pd.to_datetime(delivered["committed_date"])
    delivered["requested_date"] = pd.to_datetime(delivered["requested_date"])
    delivered["month"] = delivered["actual_delivery_date"].dt.to_period("M").astype(str)

    # Merge with shipment lines for fill rate
    first_shipments = shipment_lines[shipment_lines["is_first_shipment"] == True].copy()
    delivered_with_ship = delivered.merge(first_shipments[["so_line_id", "shipped_qty"]], on="so_line_id", how="left")

    for month, grp in delivered_with_ship.groupby("month"):
        total = len(grp)
        if total == 0:
            continue
        on_time = (grp["actual_delivery_date"] <= grp["committed_date"]).sum()
        on_time_request = (grp["actual_delivery_date"] <= grp["requested_date"]).sum()

        # OTIF
        otif_mask = (grp["actual_delivery_date"] <= grp["committed_date"]) & (grp["shipped_qty"].fillna(0) >= grp["ordered_qty"])
        otif_count = otif_mask.sum()

        # Fill rate
        fill_num = grp["shipped_qty"].fillna(0).sum()
        fill_den = grp["ordered_qty"].sum()

        truth_rows.append({
            "month": str(month),
            "on_time_delivery": round(on_time / total, 4),
            "on_time_to_request": round(on_time_request / total, 4),
            "otif": round(otif_count / total, 4),
            "unit_fill_rate": round(fill_num / fill_den, 4) if fill_den > 0 else None,
        })

    return pd.DataFrame(truth_rows)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path)


def write_data_card(stats: dict) -> None:
    card_path = OUT_DIR / "DATA_CARD.json"
    card_path.write_text(json.dumps(stats, indent=2))


def main() -> None:
    print("Generating supply chain data...")
    print(f"  Fiscal year: {FISCAL_START} to {FISCAL_END}")

    suppliers = generate_suppliers(40)
    parts = generate_parts(300)
    customers = generate_customers(120)
    carriers = generate_carriers(12)
    lanes = generate_lanes(carriers)
    storage_locs = generate_storage_locations(PLANTS)
    agreements = generate_agreements(suppliers, parts)
    tariff_codes = generate_tariff_codes(parts)
    fx_rates = generate_fx_rates()
    po_lines = generate_purchase_orders(suppliers, parts, agreements, 8000)
    receipts = generate_receipts(po_lines)
    so_lines = generate_sales_orders(customers, parts, storage_locs, 60000)
    shipments, shipment_lines = generate_shipments_and_lines(so_lines, carriers, lanes)
    delivery_events = generate_delivery_events(shipments)
    inventory = generate_inventory_snapshots(storage_locs, parts)

    truth = compute_truth_metrics(so_lines, shipment_lines, po_lines, receipts, inventory)

    # Write to four source systems with inconsistencies
    # ERP system
    write_parquet(suppliers, OUT_DIR / "erp" / "suppliers.parquet")
    write_parquet(parts, OUT_DIR / "erp" / "parts.parquet")
    write_parquet(agreements, OUT_DIR / "erp" / "agreements.parquet")
    write_parquet(po_lines, OUT_DIR / "erp" / "purchase_orders.parquet")
    write_parquet(receipts, OUT_DIR / "erp" / "goods_receipts.parquet")
    write_parquet(so_lines, OUT_DIR / "erp" / "sales_orders.parquet")
    write_parquet(inventory, OUT_DIR / "erp" / "inventory_snapshots.parquet")
    write_parquet(customers, OUT_DIR / "erp" / "customers.parquet")
    write_parquet(storage_locs, OUT_DIR / "erp" / "storage_locations.parquet")

    # TMS (transport management system)
    write_parquet(shipments, OUT_DIR / "tms" / "shipments.parquet")
    write_parquet(shipment_lines, OUT_DIR / "tms" / "shipment_lines.parquet")
    write_parquet(carriers, OUT_DIR / "tms" / "carriers.parquet")
    write_parquet(lanes, OUT_DIR / "tms" / "lanes.parquet")

    # Portal (supplier portal)
    write_parquet(delivery_events, OUT_DIR / "portal" / "delivery_events.parquet")

    # Reference data (iot-like)
    write_parquet(tariff_codes, OUT_DIR / "iot" / "tariff_codes.parquet")
    write_parquet(fx_rates, OUT_DIR / "iot" / "fx_rates.parquet")

    # Truth metrics
    write_parquet(truth, OUT_DIR / "truth_metrics.parquet")

    stats = {
        "fiscal_year": f"{FISCAL_START} to {FISCAL_END}",
        "seed": SEED,
        "suppliers": len(suppliers),
        "parts": len(parts),
        "customers": len(customers),
        "carriers": len(carriers),
        "lanes": len(lanes),
        "storage_locations": len(storage_locs),
        "agreements": len(agreements),
        "purchase_order_lines": len(po_lines),
        "goods_receipts": len(receipts),
        "sales_order_lines": len(so_lines),
        "shipments": len(shipments),
        "shipment_lines": len(shipment_lines),
        "delivery_events": len(delivery_events),
        "inventory_snapshots": len(inventory),
        "tariff_codes": len(tariff_codes),
        "truth_metric_rows": len(truth),
        "plants": len(PLANTS),
    }
    write_data_card(stats)

    print(f"\n  Data card:")
    for k, v in stats.items():
        print(f"    {k}: {v}")
    print(f"\n  Output directory: {OUT_DIR}")
    print("  Generation complete.")


if __name__ == "__main__":
    main()
