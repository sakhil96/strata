from __future__ import annotations

import json
import sys
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "out"
SEED = 20261002
FY_START = date(2025, 10, 1)
AS_OF = date(2026, 9, 30)
TARIFF_STEP = date(2026, 7, 24)
DAYS = pd.date_range(FY_START, AS_OF, freq="D")

REGION_OF = {
    "US": "US", "MX": "US", "CA": "US",
    "DE": "EMEA", "GB": "EMEA", "NL": "EMEA", "FR": "EMEA",
    "CN": "APAC", "JP": "APAC", "SG": "APAC", "IN": "APAC", "AU": "APAC",
}
TZ_OF = {
    "US": "America/Chicago", "CA": "America/Toronto", "DE": "Europe/Berlin",
    "GB": "Europe/London", "NL": "Europe/Amsterdam", "FR": "Europe/Paris",
    "SG": "Asia/Singapore", "JP": "Asia/Tokyo", "AU": "Australia/Sydney",
}

PLANTS = pd.DataFrame(
    [
        ("PLT-US01", "Joliet Assembly", "MANUFACTURING", "US", "US", "America/Chicago"),
        ("PLT-DE01", "Esslingen Werk", "MANUFACTURING", "EMEA", "DE", "Europe/Berlin"),
        ("PLT-SG01", "Tuas Fabrication", "MANUFACTURING", "APAC", "SG", "Asia/Singapore"),
        ("DC-US01", "McDonough Distribution Centre", "DISTRIBUTION", "US", "US", "America/New_York"),
        ("DC-NL01", "Venlo Distribution Centre", "DISTRIBUTION", "EMEA", "NL", "Europe/Amsterdam"),
    ],
    columns=["plant_id", "plant_name", "plant_type", "region", "country_code", "timezone"],
)

SUPPLIER_NAMES = [
    ("Hartmann Präzisionsteile GmbH", "DE"), ("Nordwerk Hydraulik GmbH", "DE"),
    ("Rheinfels Kunststoffe GmbH", "DE"), ("Bauer & Söhne Antriebstechnik GmbH", "DE"),
    ("Kessler Elektronik GmbH", "DE"), ("Halvorsen Fasteners Ltd", "GB"),
    ("Pennine Polymers Ltd", "GB"), ("Thames Valley Controls Ltd", "GB"),
    ("Corrugated Solutions of Kent Ltd", "GB"), ("Abbott Motion Systems Ltd", "GB"),
    ("Lakeshore Components Inc", "US"), ("Great Plains Packaging Inc", "US"),
    ("Cascade Power Electronics Inc", "US"), ("Redwood Bearing Co", "US"),
    ("Tri-County Fastener Supply Inc", "US"), ("Industrias Metálicas del Bajío SA de CV", "MX"),
    ("Grupo Plastimex SA de CV", "MX"), ("Ensambles Electrónicos de Monterrey SA de CV", "MX"),
    ("Empaques del Norte SA de CV", "MX"), ("Transmisiones Querétaro SA de CV", "MX"),
    ("Shenzhen Huaxin Electronics Co Ltd", "CN"), ("Ningbo Zhenhai Fastener Co Ltd", "CN"),
    ("Suzhou Yongda Precision Motion Co Ltd", "CN"), ("Dongguan Lianfa Plastics Co Ltd", "CN"),
    ("Xiamen Heng'an Packaging Co Ltd", "CN"), ("Sakura Seimitsu KK", "JP"),
    ("Nagoya Drive Systems KK", "JP"), ("Kansai Denshi Kogyo KK", "JP"),
    ("Hokuriku Resin KK", "JP"), ("Tohoku Fastening KK", "JP"),
    ("Jurong Precision Engineering Pte Ltd", "SG"), ("Straits Polymer Pte Ltd", "SG"),
    ("Tuas Power Modules Pte Ltd", "SG"), ("Marina Packaging Pte Ltd", "SG"),
    ("Kallang Motion Pte Ltd", "SG"), ("Pune Forge & Fasteners Pvt Ltd", "IN"),
    ("Chennai Circuit Works Pvt Ltd", "IN"), ("Gujarat Polychem Pvt Ltd", "IN"),
    ("Bengaluru Drives Pvt Ltd", "IN"), ("Haryana Cartons Pvt Ltd", "IN"),
]
CURRENCY_OF = {"DE": "EUR", "GB": "EUR", "SG": "SGD"}

FAMILIES = [
    ("Fasteners and fittings", "Mechanical", "7318.15",
     ["Hex flange bolt M{n}", "Socket cap screw M{n}", "Nyloc nut M{n}", "Compression fitting {n} mm"]),
    ("Motion components", "Mechanical", "8483.10",
     ["Deep groove bearing 6{n}", "Timing pulley T{n}", "Linear guide rail {n}0 mm", "Shaft coupling {n} mm"]),
    ("Control electronics", "Electrical", "8537.10",
     ["PLC I/O module {n}", "Proximity sensor M{n}", "Relay board {n}-ch", "HMI panel {n} in"]),
    ("Power electronics", "Electrical", "8504.40",
     ["DC power supply {n}0 W", "Variable frequency drive {n} kW", "Contactor {n} A", "Line reactor {n} A"]),
    ("Engineering polymers", "Materials", "3907.40",
     ["Polycarbonate sheet {n} mm", "PA66 pellets GF{n}", "POM rod {n} mm", "PTFE gasket {n} mm"]),
    ("Packaging", "Materials", "4819.10",
     ["Corrugated carton {n}00 mm", "Stretch film {n} um", "Foam insert {n}", "Pallet collar {n}00 mm"]),
]
STEPPED_FAMILIES = {"Control electronics", "Power electronics", "Engineering polymers"}

SEGMENTS = ["Industrial", "Retail", "Government", "Healthcare"]
CUSTOMER_COUNTRIES = ["US", "US", "CA", "DE", "FR", "GB", "NL", "SG", "JP", "AU"]
CUSTOMER_STEMS = [
    "Meridian", "Calder", "Ashford", "Brightwater", "Kestrel", "Northgate", "Halcyon",
    "Linden", "Oakridge", "Pembroke", "Quayside", "Riverton", "Stanmore", "Thornbury",
    "Vantage", "Westbrook", "Albion", "Beacon", "Corvid", "Dunmore",
]
CUSTOMER_KINDS = {
    "Industrial": ["Machine Works", "Automation", "Fabrication"],
    "Retail": ["Home Stores", "Trade Supply", "Outlets"],
    "Government": ["Transit Authority", "Public Works", "Defence Logistics"],
    "Healthcare": ["Medical Devices", "Hospital Supply", "Diagnostics"],
}

CARRIERS = pd.DataFrame(
    [
        ("CAR-01", "Lakeland Freight Lines", "ROAD", "LKFL", "US", "USD"),
        ("CAR-02", "Prairie Express", "ROAD", "PRXP", "US", "USD"),
        ("CAR-03", "Continental Parcel", "PARCEL", "CNPC", "US", "USD"),
        ("CAR-04", "Atlas Air Cargo", "AIR", "ATAC", "US", "USD"),
        ("CAR-05", "Rhein-Main Spedition", "ROAD", "RMSP", "EMEA", "EUR"),
        ("CAR-06", "Nordsee Logistik", "ROAD", "NSLG", "EMEA", "EUR"),
        ("CAR-07", "Benelux Pakket", "PARCEL", "BXPK", "EMEA", "EUR"),
        ("CAR-08", "Euro Air Freight", "AIR", "EUAF", "EMEA", "EUR"),
        ("CAR-09", "Lion City Haulage", "ROAD", "LCHL", "APAC", "SGD"),
        ("CAR-10", "Pacific Rim Air", "AIR", "PRAR", "APAC", "SGD"),
        ("CAR-11", "Straits Parcel", "PARCEL", "STPC", "APAC", "SGD"),
        ("CAR-12", "Oceanic Forwarding", "OCEAN", "OCFW", "APAC", "SGD"),
    ],
    columns=["carrier_id", "carrier_name", "carrier_type", "scac_code", "home_region", "billing_currency"],
)


def registry_constants() -> dict:
    registry = yaml.safe_load((ROOT / "ontology" / "metrics.yaml").read_text())
    return registry["constants"]


def build_fx(rng: np.random.Generator) -> pd.DataFrame:
    eur = 1.08 + np.cumsum(rng.normal(0, 0.0025, len(DAYS)))
    sgd = 0.74 + np.cumsum(rng.normal(0, 0.0012, len(DAYS)))
    frames = []
    for ccy, path in (("EUR", eur), ("SGD", sgd), ("USD", np.ones(len(DAYS)))):
        frames.append(pd.DataFrame({
            "fx_date": DAYS.date, "from_currency": ccy, "to_currency": "USD",
            "rate": np.round(path, 6),
        }))
    return pd.concat(frames, ignore_index=True)


def build_suppliers(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i, (name, country) in enumerate(SUPPLIER_NAMES):
        n = i + 1
        group_head = (i // 4) * 4 + 1
        rows.append({
            "supplier_id": f"SUP-{n:04d}",
            "supplier_name": name,
            "supplier_site": f"{country}-{['N', 'S', 'E', 'W'][i % 4]}{i % 3 + 1}",
            "parent_supplier_id": f"SUP-{group_head:04d}",
            "country_code": country,
            "currency": CURRENCY_OF.get(country, "USD"),
            "contact_name": f"{['A.', 'M.', 'J.', 'S.', 'K.'][i % 5]} {name.split()[0]}",
            "contact_email": f"orders@{name.split()[0].lower().replace('&', '')}.example",
            "bank_account": f"XX{rng.integers(10, 99)}{rng.integers(10**11, 10**12 - 1)}",
        })
    return pd.DataFrame(rows)


def build_parts(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i in range(300):
        family, category, hts, patterns = FAMILIES[i % len(FAMILIES)]
        size = 4 + (i // len(FAMILIES)) % 47
        pack = int(rng.choice([1, 6, 12, 24]))
        rows.append({
            "part_id": f"PRT-{i + 1:05d}",
            "part_name": patterns[(i // len(FAMILIES)) % len(patterns)].format(n=size),
            "part_family": family,
            "category": category,
            "base_uom": "EA",
            "pack_factor": pack,
            "cases_per_pallet": int(rng.choice([20, 40, 60])),
            "weight_kg": round(float(rng.uniform(0.05, 12.0)), 3),
            "std_cost_usd": round(float(rng.uniform(2.0, 400.0)), 2),
            "hts_code": f"{hts}.{(i % 9) + 1}0",
        })
    return pd.DataFrame(rows)


def build_customers(rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i in range(120):
        segment = SEGMENTS[i % 4]
        account = i // 4
        stem = CUSTOMER_STEMS[account % len(CUSTOMER_STEMS)]
        kind = CUSTOMER_KINDS[segment][account % 3]
        country = CUSTOMER_COUNTRIES[(i * 7) % len(CUSTOMER_COUNTRIES)]
        rows.append({
            "customer_id": f"SHP-{i + 1:05d}",
            "customer_name": f"{stem} {kind} {['North', 'Central', 'South', 'Harbour', 'East', 'West'][i % 6]}",
            "sold_to_id": f"SLD-{i // 2 + 1:04d}",
            "account_id": f"ACC-{account + 1:03d}",
            "account_name": f"{stem} {kind}",
            "segment": segment,
            "country_code": country,
            "region": REGION_OF[country],
            "contact_name": f"Buyer {i + 1:03d}",
            "contact_email": f"purchasing{i + 1:03d}@{stem.lower()}.example",
        })
    return pd.DataFrame(rows)


def build_locations() -> pd.DataFrame:
    rows = []
    for _, plant in PLANTS.iterrows():
        for j, kind in enumerate(["RACK", "BULK", "COLD"]):
            rows.append({
                "storage_location_id": f"{plant.plant_id}-{kind[0]}{j + 1}",
                "storage_location_name": f"{plant.plant_name} {kind.lower()} store",
                "plant_id": plant.plant_id,
                "location_type": kind,
            })
    return pd.DataFrame(rows)


def build_tariffs(parts: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for _, part in parts.iterrows():
        base = round(float(rng.uniform(0.0, 0.06)), 4)
        stepped = part.part_family in STEPPED_FAMILIES
        post = round(base + float(rng.uniform(0.05, 0.15)), 4) if stepped else base
        rows.append((part.part_id, part.hts_code, base, FY_START, TARIFF_STEP - timedelta(days=1)))
        rows.append((part.part_id, part.hts_code, post, TARIFF_STEP, AS_OF))
    return pd.DataFrame(rows, columns=["part_id", "hts_code", "duty_rate", "effective_from", "effective_to"])


def fx_lookup(fx: pd.DataFrame):
    table = {(r.from_currency, r.fx_date): r.rate for r in fx.itertuples()}
    return lambda ccy, d: table[(ccy, d)]


def local_to_utc(d: date, hour: float, tz: str) -> datetime:
    local = datetime.combine(d, time(0, 0)) + timedelta(minutes=round(hour * 60))
    return local.replace(tzinfo=ZoneInfo(tz)).astimezone(UTC).replace(tzinfo=None)


def build_sales(rng, customers, parts, locations, carriers):
    combos = []
    for loc in locations.itertuples():
        picks = rng.choice(len(parts), size=40, replace=False)
        combos.extend((loc.storage_location_id, loc.plant_id, parts.part_id.iloc[p]) for p in sorted(picks))
    combos = pd.DataFrame(combos, columns=["storage_location_id", "plant_id", "part_id"])
    plant_region = dict(zip(PLANTS.plant_id, PLANTS.region, strict=False))
    pack = dict(zip(parts.part_id, parts.pack_factor, strict=False))

    line_rows, ship_rows, ship_line_rows = [], [], []
    n_orders = 15000
    order_days = rng.integers(0, (AS_OF - FY_START).days - 3, size=n_orders)
    ship_seq = 0
    customer_rows = customers.to_dict("records")
    home_plants = {r: PLANTS[PLANTS.region == r].plant_id.tolist() for r in PLANTS.region.unique()}
    all_plants = PLANTS.plant_id.to_numpy()
    locs_at = {p: locations[locations.plant_id == p].storage_location_id.to_numpy() for p in all_plants}
    parts_at = {loc: g.part_id.to_numpy() for loc, g in combos.groupby("storage_location_id")}
    carriers_in = {r: g.to_dict("records") for r, g in carriers.groupby("home_region")}
    for o in range(n_orders):
        cust = customer_rows[int(rng.integers(0, len(customer_rows)))]
        home = home_plants.get(cust["region"], [])
        plant = rng.choice(home) if home and rng.random() < 0.85 else rng.choice(all_plants)
        loc = rng.choice(locs_at[plant])
        loc_parts = parts_at[loc]
        n_lines = int(rng.integers(3, 6))
        chosen = rng.choice(loc_parts, size=n_lines, replace=False)

        order_date = FY_START + timedelta(days=int(order_days[o]))
        requested = order_date + timedelta(days=int(rng.integers(6, 22)))
        committed = requested + timedelta(days=int(rng.choice([0, 0, 0, 1, 1, 2, 3])))
        cross = plant_region[plant] != cust["region"]
        transit = 4 if cross else 2
        ship_date = committed - timedelta(days=transit) + timedelta(
            days=int(rng.choice([-2, -1, -1, -1, -1, -1, -1, -1, 0, 0, 1])))
        ship_date = max(ship_date, order_date + timedelta(days=1))
        delivery = ship_date + timedelta(days=transit + int(rng.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2])))
        eta = ship_date + timedelta(days=transit + 1)
        home_carriers = carriers_in[plant_region[plant]]
        carrier = home_carriers[int(rng.integers(0, len(home_carriers)))]
        so = f"SO-{o + 1:07d}"

        first_lines, backorder_lines = [], []
        for k, part_id in enumerate(chosen):
            qty = int(rng.integers(1, 41)) * pack[part_id]
            cancelled = rng.random() < 0.04
            first_qty = 0 if cancelled else qty
            if not cancelled and rng.random() < 0.07:
                first_qty = int(qty * float(rng.uniform(0.5, 0.95)))
            line = {
                "so_line_id": f"{so}-{(k + 1) * 10:03d}", "so_number": so, "line_number": (k + 1) * 10,
                "customer_id": cust["customer_id"], "part_id": part_id, "storage_location_id": loc,
                "plant_id": plant, "ordered_qty": qty, "order_date": order_date,
                "requested_date": requested, "committed_date": committed, "is_cancelled": cancelled,
            }
            line_rows.append(line)
            if not cancelled:
                first_lines.append((line["so_line_id"], part_id, first_qty))
                if first_qty < qty:
                    backorder_lines.append((line["so_line_id"], part_id, qty - first_qty))

        legs = [(ship_date, delivery, eta, first_lines, 1)]
        if backorder_lines:
            later = timedelta(days=int(rng.integers(7, 15)))
            legs.append((ship_date + later, delivery + later, eta + later, backorder_lines, 2))
        for depart, pod, carrier_eta, legs_lines, seq in legs:
            if not legs_lines or depart > AS_OF:
                continue
            ship_seq += 1
            sid = f"SHP{ship_seq:07d}"
            ship_rows.append({
                "shipment_id": sid, "carrier_id": carrier["carrier_id"], "origin_plant_id": plant,
                "customer_id": cust["customer_id"], "ship_date": depart, "carrier_eta": carrier_eta,
                "actual_delivery": pod if pod <= AS_OF else None, "is_cross_region": cross,
                "billing_currency": carrier["billing_currency"],
            })
            for so_line_id, part_id, qty in legs_lines:
                ship_line_rows.append({
                    "shipment_line_id": f"{sid}-{len(ship_line_rows) % 1000:03d}", "shipment_id": sid,
                    "so_line_id": so_line_id, "part_id": part_id, "shipped_qty": qty,
                    "shipment_seq": seq,
                })

    lines = pd.DataFrame(line_rows)
    shipments = pd.DataFrame(ship_rows)
    ship_lines = pd.DataFrame(ship_line_rows)
    ship_lines["shipment_line_id"] = [f"SL{i + 1:08d}" for i in range(len(ship_lines))]
    return combos, lines, shipments, ship_lines


def price_freight(shipments, ship_lines, parts, fx_of):
    weight = dict(zip(parts.part_id, parts.weight_kg, strict=False))
    ship_lines = ship_lines.copy()
    ship_lines["line_weight_kg"] = ship_lines.part_id.map(weight) * ship_lines.shipped_qty
    totals = ship_lines.groupby("shipment_id").line_weight_kg.sum()
    shipments = shipments.copy()
    shipments["chargeable_weight_kg"] = shipments.shipment_id.map(totals).round(1)
    usd = np.where(shipments.is_cross_region, 600 + 4.2 * shipments.chargeable_weight_kg,
                   180 + 0.9 * shipments.chargeable_weight_kg)
    rates = [fx_of(c, d) for c, d in zip(shipments.billing_currency, shipments.ship_date, strict=False)]
    shipments["freight_charge"] = np.round(usd / np.array(rates), 2)
    shipments["freight_usd"] = shipments.freight_charge * np.array(rates)
    share = ship_lines.line_weight_kg / ship_lines.shipment_id.map(totals)
    ship_lines["freight_alloc_usd"] = share * ship_lines.shipment_id.map(
        shipments.set_index("shipment_id").freight_usd)
    return shipments, ship_lines


def build_events(rng, shipments, customers, carriers):
    tz_cust = dict(zip(customers.customer_id, customers.country_code.map(TZ_OF), strict=False))
    tz_plant = dict(zip(PLANTS.plant_id, PLANTS.timezone, strict=False))
    rows, transit = [], {}
    as_of_end = datetime.combine(AS_OF, time(23, 59))
    for s in shipments.itertuples():
        origin_tz, dest_tz = tz_plant[s.origin_plant_id], tz_cust[s.customer_id]
        picked = local_to_utc(s.ship_date, 6 + float(rng.integers(0, 16)) / 4, origin_tz)
        stamps = [("picked_up", picked, origin_tz)]
        if s.actual_delivery is not None:
            delivered = local_to_utc(s.actual_delivery, 9 + float(rng.integers(0, 32)) / 4, dest_tz)
            delivered = max(delivered, picked + timedelta(hours=6))
            transit[s.shipment_id] = (delivered - picked).total_seconds() / 3600
            span = delivered - picked
        else:
            delivered, span = None, as_of_end - picked
        n_mid = int(rng.integers(3, 7))
        for j in range(n_mid):
            when = picked + span * (j + 1) / (n_mid + 1)
            kind = "exception" if rng.random() < 0.04 else ("departed" if j % 2 == 0 else "arrived")
            stamps.append((kind, when.replace(second=0, microsecond=0), origin_tz if j < n_mid / 2 else dest_tz))
        if delivered is not None:
            stamps.append(("delivered", delivered, dest_tz))
        for kind, when, tz in stamps:
            if when > as_of_end:
                continue
            rows.append((s.shipment_id, kind, when, tz, when))
            if kind == "delivered" and rng.random() < 0.12:
                rows.append((s.shipment_id, kind, when + timedelta(days=2), tz, when + timedelta(days=2, hours=3)))
    events = pd.DataFrame(rows, columns=["shipment_id", "event_type", "event_time_utc", "site_tz", "received_at"])
    events.insert(0, "event_id", [f"EV{i + 1:08d}" for i in range(len(events))])
    shipments = shipments.copy()
    shipments["transit_hours"] = shipments.shipment_id.map(transit)
    return events, shipments


def build_inventory(rng, combos, ship_lines, lines, parts):
    cost = dict(zip(parts.part_id, parts.std_cost_usd, strict=False))
    shipped = ship_lines.merge(lines[["so_line_id", "storage_location_id"]], on="so_line_id")
    day_index = {d: i for i, d in enumerate(DAYS.date)}
    rows = []
    for c in combos.itertuples():
        demand = np.zeros(len(DAYS))
        mine = shipped[(shipped.storage_location_id == c.storage_location_id) & (shipped.part_id == c.part_id)]
        for d, q in zip(mine.ship_date, mine.shipped_qty, strict=False):
            demand[day_index[d]] += q
        daily = max(demand.mean(), 1.0)
        on_hand = round(daily * 30)
        reorder, order_up_to = daily * 6, daily * 40
        arrivals = {}
        for i in range(len(DAYS)):
            on_hand += arrivals.pop(i, 0)
            on_hand = max(0, on_hand - int(demand[i]))
            if on_hand < reorder and not arrivals:
                arrivals[i + int(rng.integers(4, 11))] = round(order_up_to - on_hand)
            allocated = int(demand[i + 1:i + 4].sum())
            rows.append((c.storage_location_id, c.plant_id, c.part_id, DAYS[i].date(), on_hand,
                         on_hand * cost[c.part_id], allocated, demand[i], demand[i] * cost[c.part_id]))
    return pd.DataFrame(rows, columns=[
        "storage_location_id", "plant_id", "part_id", "snapshot_date", "on_hand_qty",
        "on_hand_value_std", "allocated_qty", "shipped_qty", "cogs_usd"])


def build_procurement(rng, suppliers, parts, fx_of, tariffs, constants):
    plant_region = dict(zip(PLANTS.plant_id, PLANTS.region, strict=False))
    plant_country = dict(zip(PLANTS.plant_id, PLANTS.country_code, strict=False))
    weight = dict(zip(parts.part_id, parts.weight_kg, strict=False))
    pack = dict(zip(parts.part_id, parts.pack_factor, strict=False))
    tariff_rows = tariffs.sort_values(["part_id", "effective_from"]).itertuples()
    tariff_of = {}
    for t in tariff_rows:
        tariff_of.setdefault(t.part_id, []).append((t.effective_from, t.effective_to, t.duty_rate))

    agreements = []
    for s in suppliers.itertuples():
        for p in sorted(rng.choice(len(parts), size=int(rng.integers(6, 14)), replace=False)):
            part = parts.iloc[p]
            agreements.append({
                "agreement_id": f"AGR-{len(agreements) + 1:05d}", "supplier_id": s.supplier_id,
                "part_id": part.part_id, "currency": s.currency,
                "unit_cost": round(part.std_cost_usd * float(rng.uniform(0.55, 0.85))
                                   / (1.08 if s.currency == "EUR" else 0.74 if s.currency == "SGD" else 1), 4),
                "incoterm": str(rng.choice(["EXW", "FCA", "FOB", "CIF", "DAP"])),
                "quoted_lead_days": int(rng.integers(21, 56)),
                "effective_from": FY_START, "effective_to": AS_OF,
            })
    agreements = pd.DataFrame(agreements)
    by_supplier = {k: g for k, g in agreements.groupby("supplier_id")}

    po_lines, inbound = [], []
    po_no, n_lines = 0, 0
    while n_lines < 8000:
        po_no += 1
        supplier = suppliers.iloc[int(rng.integers(0, len(suppliers)))]
        plant = str(rng.choice(PLANTS.plant_id))
        order_date = FY_START + timedelta(days=int(rng.integers(0, 330)))
        offer = by_supplier[supplier.supplier_id]
        k = min(int(rng.integers(1, 6)), len(offer))
        picks = offer.iloc[sorted(rng.choice(len(offer), size=k, replace=False))]
        lead = int(picks.quoted_lead_days.max())
        promised = order_date + timedelta(days=lead)
        confirmed = promised + timedelta(days=int(rng.choice([0, 0, 1, 2, -1])))
        receipt = promised + timedelta(days=int(rng.choice([-4, -3, -2, -2, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 1, 3])))
        cross = REGION_OF[supplier.country_code] != plant_region[plant]
        transit = 18 if cross else 3
        depart = max(order_date + timedelta(days=1), receipt - timedelta(days=transit))
        received = receipt <= AS_OF
        po = f"45{po_no:08d}"
        fx_rate = fx_of(supplier.currency, order_date)
        lines = []
        for j, a in enumerate(picks.itertuples()):
            qty = int(rng.integers(5, 120)) * pack[a.part_id]
            cancelled = rng.random() < 0.03
            got = 0 if cancelled or not received else qty
            if got and rng.random() < 0.08:
                got = int(qty * float(rng.uniform(0.5, 0.95)))
            lines.append({
                "po_line_id": f"{po}-{(j + 1) * 10:05d}", "po_number": po, "line_number": (j + 1) * 10,
                "supplier_id": supplier.supplier_id, "part_id": a.part_id, "plant_id": plant,
                "ordered_qty": qty, "unit_cost": a.unit_cost, "currency": supplier.currency,
                "order_date": order_date, "promised_date": promised, "confirmed_date": confirmed,
                "is_cancelled": cancelled, "receipt_date": receipt if got else None, "received_qty": got,
                "ship_date": depart, "fx_rate": fx_rate,
                "is_import": supplier.country_code != plant_country[plant],
                "line_weight_kg": got * weight[a.part_id],
            })
        total_w = sum(line["line_weight_kg"] for line in lines)
        if total_w > 0 and depart <= AS_OF:
            usd = (250 + 3.1 * total_w) if cross else (90 + 0.6 * total_w)
            depart_rate = fx_of(supplier.currency, depart)
            charge = round(usd / depart_rate, 2)
            inbound.append({"inbound_id": f"IN{po_no:07d}", "po_number": po, "ship_date": depart,
                            "freight_charge": charge, "freight_currency": supplier.currency})
            for line in lines:
                line["freight_usd"] = charge * depart_rate * line["line_weight_kg"] / total_w
        for line in lines:
            line.setdefault("freight_usd", 0.0)
            material = line["unit_cost"] * line["received_qty"] * fx_rate
            rate = next(r for f, t, r in tariff_of[line["part_id"]] if f <= depart <= t) if depart <= AS_OF else 0.0
            line["material_usd"] = material
            line["duty_usd"] = rate * material if line["is_import"] else 0.0
            line["insurance_usd"] = constants["insurance_rate"] * material
            line["handling_usd"] = constants["handling_usd_per_unit"] * line["received_qty"]
            line["landed_usd"] = (material + line["freight_usd"] + line["duty_usd"]
                                  + line["insurance_usd"] + line["handling_usd"])
            po_lines.append(line)
            n_lines += 1
    return agreements, pd.DataFrame(po_lines), pd.DataFrame(inbound)


EXCEPTION_CAUSES = [
    ("carrier_delay", "Linehaul missed its cut-off at {hub}; carrier re-booked on the next departure.", True),
    ("customs_hold", "Held at {hub} customs for documentation; commercial invoice re-issued with HS code corrected.", True),
    ("damage_in_transit", "Two cartons crushed on arrival at {hub}; consignee signed with remarks, claim opened.", True),
    ("address_issue", "Dock closed at the ship-to address; delivery re-attempted the next morning.", True),
    ("weather", "Storm closure on the {hub} corridor; carrier held freight at the terminal for safety.", True),
    ("documentation", "POD scan illegible; carrier re-sent the signed delivery note, no change to delivery.", False),
]
HUBS = ["Memphis", "Duisburg", "Rotterdam", "Changi", "Laredo", "Antwerp", "Louisville", "Leipzig"]
CLAUSES = [
    ("lead_time_commitment", "Lead time",
     "Supplier shall deliver within {lead} calendar days of a firm purchase order under {incoterm} terms."),
    ("late_delivery_penalty", "Late delivery",
     "For each full week of delay beyond the confirmed date, Buyer may deduct 1.5% of the line value, capped at 7.5%."),
    ("price_adjustment", "Price review",
     "Unit prices in {ccy} are fixed for the fiscal year and reviewed on 1 October against the agreed index."),
    ("quality", "Quality",
     "Lots failing incoming inspection are returned at Supplier's cost and do not count as delivered."),
    ("force_majeure", "Force majeure",
     "Neither party is liable for delay caused by events beyond reasonable control, notified within 5 business days."),
]
PROCEDURES = [
    ("Receiving against a purchase order", "Match the delivery note to the PO line before posting a goods receipt. "
     "Post the receipt on the date the goods arrive, not the date the paperwork is cleared; receipt date drives supplier on-time receipt."),
    ("Recording a delivery exception", "Every exception event needs a note naming the cause, the hub and whether the customer will notice. "
     "Notes are searchable by the agent and quoted, never turned into metrics."),
    ("Cycle counting in distribution centres", "Count in eaches where the label shows eaches and in cases where it shows cases. "
     "The conformed model converts cases with the material master's pack factor."),
    ("Changing a committed date", "A committed date may move only with the customer's written agreement. "
     "The original commitment stays on the line; on-time delivery is measured against the latest agreed date."),
    ("Cancelling an order line", "Set the rejection reason rather than deleting the line. Cancelled lines are excluded from both "
     "the numerator and the denominator of every delivery and fill metric."),
    ("Booking cross-region freight", "Book ocean or air through a contracted carrier; the carrier's ETA is their estimate, "
     "not our commitment, and is measured separately as carrier on-time."),
    ("Handling a tariff change", "When a duty rate changes, the new rate applies to goods that leave the supplier on or after "
     "the effective date. Update the material tariff table; landed cost follows automatically."),
    ("Escalating a stockout", "A location-part-day with demand allocated and nothing on hand is a stockout. "
     "Escalate to the planner for the plant within one working day."),
]


def build_documents(rng, events, shipments, agreements, suppliers):
    rows = []
    eta = dict(zip(shipments.shipment_id, shipments.carrier_eta, strict=False))
    pod = dict(zip(shipments.shipment_id, shipments.actual_delivery, strict=False))
    exceptions = events[events.event_type == "exception"].reset_index(drop=True)
    for i, e in exceptions.iterrows():
        cause, text, visible = EXCEPTION_CAUSES[int(rng.integers(0, len(EXCEPTION_CAUSES)))]
        late = pod[e.shipment_id] is not None and pod[e.shipment_id] > eta[e.shipment_id]
        rows.append({
            "doc_id": f"EXC-{i + 1:06d}", "kind": "exception_note", "related_id": e.shipment_id,
            "title": f"Exception on {e.shipment_id}, {e.event_time_utc:%d %b %Y}",
            "body": text.format(hub=HUBS[int(rng.integers(0, len(HUBS)))]),
            "category": cause, "is_customer_impacting": bool(visible and late), "source_system": "portal",
        })
    names = dict(zip(suppliers.supplier_id, suppliers.supplier_name, strict=False))
    for a in agreements.itertuples():
        for key, heading, text in CLAUSES:
            rows.append({
                "doc_id": f"CLS-{a.agreement_id}-{key[:4].upper()}", "kind": "contract_clause",
                "related_id": a.agreement_id, "title": f"{heading}, {names[a.supplier_id]}",
                "body": text.format(lead=a.quoted_lead_days, incoterm=a.incoterm, ccy=a.currency),
                "category": key, "is_customer_impacting": False, "source_system": "erp",
            })
    for j, (title, body) in enumerate(PROCEDURES, 1):
        rows.append({"doc_id": f"SOP-{j:03d}", "kind": "operating_procedure", "related_id": None, "title": title,
                     "body": body, "category": "procedure", "is_customer_impacting": False, "source_system": "content"})
    return pd.DataFrame(rows)


def month_of(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series).dt.to_period("M").dt.to_timestamp().dt.date


def grouped(frame, metric, dims, kind, num=None, den=None, value=None):
    frame = frame[frame.month.notna() & (frame.month <= date(AS_OF.year, AS_OF.month, 1))]
    sets = [[]] + [[d] for d in dims] + ([dims] if len(dims) > 1 else [])
    out = []
    for extra in sets:
        keys = ["month", *extra]
        g = frame.groupby(keys, dropna=False)
        if kind == "ratio":
            agg = g.agg(numerator=(num, "sum"), denominator=(den, "sum")).reset_index()
            agg = agg[agg.denominator != 0]
            agg["value"] = agg.numerator / agg.denominator
        elif kind == "median":
            agg = g[value].median().rename("value").reset_index()
        else:
            agg = g[value].std(ddof=1).rename("value").reset_index()
        agg["metric"] = metric
        agg["grouping"] = ",".join(keys)
        out.append(agg)
    return out


def compute_truth(lines, shipments, ship_lines, inventory, po_lines, customers, parts):
    region = dict(zip(PLANTS.plant_id, PLANTS.region, strict=False))
    segment = dict(zip(customers.customer_id, customers.segment, strict=False))
    family = dict(zip(parts.part_id, parts.part_family, strict=False))
    first = ship_lines[ship_lines.shipment_seq == 1].merge(
        shipments[["shipment_id", "ship_date", "actual_delivery"]], on="shipment_id")
    sl = lines.merge(first[["so_line_id", "shipped_qty", "actual_delivery"]], on="so_line_id", how="left")
    sl["first_qty"] = sl.shipped_qty.fillna(0)
    sl["region"] = sl.plant_id.map(region)
    sl["segment"] = sl.customer_id.map(segment)
    sl["part_family"] = sl.part_id.map(family)
    live = ~sl.is_cancelled
    delivered = live & sl.actual_delivery.notna()
    sl["delivered"] = delivered.astype(int)
    sl["on_time"] = (delivered & (sl.actual_delivery <= sl.committed_date)).astype(int)
    sl["on_time_req"] = (delivered & (sl.actual_delivery <= sl.requested_date)).astype(int)
    sl["otif"] = (sl.on_time.astype(bool) & (sl.first_qty >= sl.ordered_qty)).astype(int)
    sl["live_ordered"] = np.where(live, sl.ordered_qty, 0)
    sl["live_first"] = np.where(live, sl.first_qty, 0)
    sl["line_filled"] = (live & (sl.first_qty >= sl.ordered_qty)).astype(int)
    sl["live_line"] = live.astype(int)
    sl["cycle_days"] = [(a - o).days if d else np.nan
                        for a, o, d in zip(sl.actual_delivery, sl.order_date, delivered, strict=False)]

    dims_so = ["plant_id", "region", "segment", "part_family"]
    by_delivery = sl.assign(month=month_of(sl.actual_delivery.where(delivered)))
    by_request = sl.assign(month=month_of(sl.requested_date))
    orders = by_request[by_request.live_line == 1].groupby("so_number").agg(
        month=("month", "first"), plant_id=("plant_id", "first"), region=("region", "first"),
        segment=("segment", "first"), filled=("line_filled", "min")).reset_index()
    orders["one"] = 1

    parts_out = []
    parts_out += grouped(by_delivery, "on_time_delivery", dims_so, "ratio", "on_time", "delivered")
    parts_out += grouped(by_delivery, "on_time_to_request", dims_so, "ratio", "on_time_req", "delivered")
    parts_out += grouped(by_delivery, "otif", dims_so, "ratio", "otif", "delivered")
    parts_out += grouped(by_delivery[by_delivery.delivered == 1], "order_fulfilment_cycle_days",
                         dims_so, "median", value="cycle_days")
    parts_out += grouped(by_request, "unit_fill_rate", dims_so, "ratio", "live_first", "live_ordered")
    parts_out += grouped(by_request, "line_fill_rate", dims_so, "ratio", "line_filled", "live_line")
    parts_out += grouped(orders, "order_fill_rate", ["plant_id", "region", "segment"], "ratio", "filled", "one")

    sh = shipments.copy()
    sh["region"] = sh.origin_plant_id.map(region)
    sh["plant_id"] = sh.origin_plant_id
    sh["segment"] = sh.customer_id.map(segment)
    sh["delivered"] = sh.actual_delivery.notna().astype(int)
    sh["on_eta"] = (sh.actual_delivery.notna() & (sh.actual_delivery <= sh.carrier_eta)).astype(int)
    sh["month"] = month_of(sh.actual_delivery)
    dims_sh = ["plant_id", "region", "segment"]
    parts_out += grouped(sh, "carrier_on_time", dims_sh, "ratio", "on_eta", "delivered")
    parts_out += grouped(sh[sh.delivered == 1], "transit_hours", dims_sh, "median", value="transit_hours")

    fl = ship_lines.merge(sh[["shipment_id", "ship_date", "plant_id", "region", "segment"]], on="shipment_id")
    fl["part_family"] = fl.part_id.map(family)
    fl["month"] = month_of(fl.ship_date)
    parts_out += grouped(fl, "freight_cost_per_unit", dims_so, "ratio", "freight_alloc_usd", "shipped_qty")

    po = po_lines.copy()
    po["region"] = po.plant_id.map(region)
    po["part_family"] = po.part_id.map(family)
    received = po.received_qty > 0
    po["month"] = month_of(po.receipt_date)
    po["received_line"] = received.astype(int)
    po["on_time_receipt"] = (received & (po.receipt_date <= po.promised_date)).astype(int)
    po["lead_days"] = [(r - o).days if ok else np.nan for r, o, ok in zip(po.receipt_date, po.order_date, received, strict=False)]
    dims_po = ["plant_id", "region", "part_family"]
    parts_out += grouped(po, "supplier_on_time_receipt", dims_po, "ratio", "on_time_receipt", "received_line")
    parts_out += grouped(po, "landed_cost_per_unit", dims_po, "ratio", "landed_usd", "received_qty")
    parts_out += grouped(po[received], "supplier_lead_time_days", dims_po, "median", value="lead_days")
    parts_out += grouped(po[received], "lead_time_variability", dims_po, "std", value="lead_days")

    inv = inventory_months(inventory)
    inv["region"] = inv.plant_id.map(region)
    inv["part_family"] = inv.part_id.map(family)
    dims_inv = ["plant_id", "region", "part_family"]
    inv["cogs_daily_90d"] = inv.cogs_90d / 90
    inv["units_daily_90d"] = inv.units_90d / 90
    inv["cogs_annual_90d"] = inv.cogs_90d / 90 * 365
    parts_out += grouped(inv, "days_of_inventory", dims_inv, "ratio", "on_hand_value_end", "cogs_daily_90d")
    parts_out += grouped(inv, "doi_units", dims_inv, "ratio", "on_hand_qty_end", "units_daily_90d")
    parts_out += grouped(inv, "inventory_turns", dims_inv, "ratio", "cogs_annual_90d", "on_hand_value_end")
    parts_out += grouped(inv, "stockout_rate", dims_inv, "ratio", "stockout_days", "obs_days")
    inv["avg_value_x_days"] = inv.avg_value_month * inv.days_in_month
    parts_out += grouped(inv, "dio_financial", dims_inv, "ratio", "avg_value_x_days", "cogs_month")

    truth = pd.concat(parts_out, ignore_index=True)
    cols = ["metric", "grouping", "month", "plant_id", "region", "segment", "part_family",
            "numerator", "denominator", "value"]
    for c in cols:
        if c not in truth:
            truth[c] = None
    truth = truth[cols]
    for c in ["plant_id", "region", "segment", "part_family"]:
        truth[c] = truth[c].astype("string")
    return truth.sort_values(cols[:7], na_position="first").reset_index(drop=True), sl, inv


def inventory_months(inventory: pd.DataFrame) -> pd.DataFrame:
    keys = ["storage_location_id", "plant_id", "part_id"]
    inv = inventory.sort_values([*keys, "snapshot_date"]).reset_index(drop=True)
    inv["month"] = month_of(inv.snapshot_date)
    inv["stockout"] = ((inv.on_hand_qty == 0) & (inv.allocated_qty > 0)).astype(int)
    rolling = (inv.groupby(keys, sort=False)[["cogs_usd", "shipped_qty"]].rolling(90, min_periods=1).sum()
               .reset_index(level=list(range(len(keys))), drop=True))
    inv["cogs_90d"] = rolling["cogs_usd"]
    inv["units_90d"] = rolling["shipped_qty"]
    by_month = inv.groupby([*keys, "month"], sort=True)
    agg = by_month.agg(
        avg_value_month=("on_hand_value_std", "mean"), cogs_month=("cogs_usd", "sum"),
        days_in_month=("snapshot_date", "count"), stockout_days=("stockout", "sum"), obs_days=("snapshot_date", "count"),
        on_hand_value_end=("on_hand_value_std", "last"), on_hand_qty_end=("on_hand_qty", "last"),
        cogs_90d=("cogs_90d", "last"), units_90d=("units_90d", "last"))
    return agg.reset_index()


def write(frame: pd.DataFrame, rel: str) -> None:
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(frame, preserve_index=False), path, compression="zstd")


def emit_sources(rng, d):
    s = d["suppliers"]
    write(s.assign(SUPPLIER_KEY=s.supplier_id.str.replace("SUP-", "SUP"))[
        ["SUPPLIER_KEY", "supplier_name", "supplier_site", "parent_supplier_id", "country_code",
         "currency", "contact_name", "contact_email", "bank_account"]].rename(columns={
            "supplier_name": "NAME1", "supplier_site": "SITE", "parent_supplier_id": "PARENT_KEY",
            "country_code": "LAND1", "currency": "WAERS", "contact_name": "CONTACT",
            "contact_email": "EMAIL", "bank_account": "IBAN"}).assign(
        PARENT_KEY=lambda f: f.PARENT_KEY.str.replace("SUP-", "SUP")), "erp/supplier_master.parquet")

    variants = []
    for row in s.itertuples():
        n = int(row.supplier_id[4:])
        name = row.supplier_name
        for suffix in ([""] if n % 3 else ["", "."]):
            shown = (name.upper().replace("Ä", "AE").replace("Ö", "OE").replace("Ü", "UE")
                     .replace("É", "E").replace("Á", "A") + suffix) if suffix else name
            variants.append({"VENDOR_REF": f"V-{n:06d}", "VENDOR_NAME": shown,
                             "PORTAL_CONTACT": row.contact_name, "PORTAL_EMAIL": row.contact_email})
    write(pd.DataFrame(variants), "portal/supplier_profiles.parquet")

    p = d["parts"]
    write(p.rename(columns={"part_id": "MATNR", "part_name": "MAKTX", "part_family": "PRODH_FAMILY",
                            "category": "PRODH_CATEGORY", "base_uom": "MEINS", "pack_factor": "EA_PER_CS",
                            "cases_per_pallet": "CS_PER_PAL", "weight_kg": "NTGEW_KG",
                            "std_cost_usd": "STPRS_USD", "hts_code": "STAWN"}), "erp/material_master.parquet")
    write(d["tariffs"].rename(columns={"part_id": "MATNR", "hts_code": "STAWN", "duty_rate": "DUTY_RATE",
                                       "effective_from": "VALID_FROM", "effective_to": "VALID_TO"}),
          "erp/material_tariffs.parquet")
    write(d["customers"], "erp/customer_master.parquet")
    write(d["locations"], "erp/storage_locations.parquet")
    write(PLANTS, "erp/plants.parquet")
    write(d["fx"], "erp/fx_rates.parquet")
    write(d["agreements"].assign(supplier_id=lambda f: f.supplier_id.str.replace("SUP-", "SUP")),
          "erp/purchasing_info_records.parquet")

    po = d["po_lines"]
    pack = dict(zip(p.part_id, p.pack_factor, strict=False))
    pallet = dict(zip(p.part_id, p.cases_per_pallet, strict=False))
    uom, qty = [], []
    for row in po.itertuples():
        per_pal = pack[row.part_id] * pallet[row.part_id]
        pick = rng.random()
        if pick < 0.15 and row.ordered_qty % per_pal == 0:
            uom.append("PAL"), qty.append(row.ordered_qty // per_pal)
        elif pick < 0.5 and pack[row.part_id] > 1:
            uom.append("CS"), qty.append(row.ordered_qty // pack[row.part_id])
        else:
            uom.append("EA"), qty.append(row.ordered_qty)
    n = po.supplier_id.str[4:].astype(int)
    legacy_key = np.where(po.index % 3 == 0, "SUP" + n.map("{:04d}".format),
                          np.where(po.index % 3 == 1, "V-" + n.map("{:06d}".format), "VENDOR_" + n.astype(str)))
    write(pd.DataFrame({
        "EBELN": po.po_number, "EBELP": po.line_number, "LIFNR": legacy_key, "MATNR": po.part_id,
        "WERKS": po.plant_id, "MENGE": qty, "MEINS": uom, "NETPR_PER_EA": po.unit_cost, "WAERS": po.currency,
        "BEDAT": po.order_date, "VENDOR_PROMISE_DT": po.promised_date, "CONFIRMED_DT": po.confirmed_date,
        "LOEKZ": np.where(po.is_cancelled, "L", ""),
    }), "erp/purchase_order_lines.parquet")
    gr = po[po.received_qty > 0]
    write(pd.DataFrame({
        "MBLNR": [f"50{i:08d}" for i in range(len(gr))], "EBELN": gr.po_number.values,
        "EBELP": gr.line_number.values, "BUDAT": gr.receipt_date.values, "QTY_EA": gr.received_qty.values,
        "QUALITY": np.where(np.arange(len(gr)) % 23 == 0, "QUARANTINE", "ACCEPTED"),
    }), "erp/goods_receipts.parquet")
    write(d["inbound"].rename(columns={"inbound_id": "INBOUND_NO", "po_number": "PO_NO",
                                       "ship_date": "DEPART_DATE", "freight_charge": "FREIGHT_AMT",
                                       "freight_currency": "FREIGHT_CCY"}), "tms/inbound_shipments.parquet")

    so = d["lines"]
    write(pd.DataFrame({
        "VBELN": so.so_number, "POSNR": so.line_number, "KUNWE": so.customer_id, "MATNR": so.part_id,
        "LGORT": so.storage_location_id, "KWMENG_EA": so.ordered_qty, "AUDAT": so.order_date,
        "REQ_DLV_DATE": so.requested_date, "CONF_DLV_DATE": so.committed_date,
        "ABGRU": np.where(so.is_cancelled, "Z1", ""),
    }), "erp/sales_order_lines.parquet")

    sh = d["shipments"]
    write(pd.DataFrame({
        "SHIPMENT_NO": sh.shipment_id, "CARRIER_SCAC": sh.carrier_id.map(dict(zip(CARRIERS.carrier_id, CARRIERS.scac_code, strict=False))),
        "ORIGIN_PLANT": sh.origin_plant_id, "SHIP_TO": sh.customer_id, "DEPART_DATE": sh.ship_date,
        "CARRIER_ETA": sh.carrier_eta, "POD_DATE": sh.actual_delivery, "FREIGHT_AMT": sh.freight_charge,
        "FREIGHT_CCY": sh.billing_currency, "CHG_WEIGHT_KG": sh.chargeable_weight_kg,
    }), "tms/shipments.parquet")
    sl = d["ship_lines"].merge(so[["so_line_id", "so_number", "line_number"]], on="so_line_id")
    write(pd.DataFrame({
        "SHIPMENT_NO": sl.shipment_id, "VBELN": sl.so_number, "POSNR": sl.line_number,
        "SHIPPED_QTY_EA": sl.shipped_qty, "LEG": sl.shipment_seq,
    }), "tms/shipment_lines.parquet")
    write(CARRIERS.drop(columns=["billing_currency"]), "tms/carriers.parquet")

    ev = d["events"]
    local, basis = [], []
    for when, tz in zip(ev.event_time_utc, ev.site_tz, strict=False):
        aware = when.replace(tzinfo=UTC).astimezone(ZoneInfo(tz))
        naive = aware.replace(tzinfo=None)
        roundtrip = naive.replace(tzinfo=ZoneInfo(tz)).astimezone(UTC).replace(tzinfo=None)
        if rng.random() < 0.4 and roundtrip == when:
            local.append(naive), basis.append("LOCAL")
        else:
            local.append(when), basis.append("UTC")
    code = {"picked_up": "PU", "departed": "DEP", "arrived": "ARR", "delivered": "POD", "exception": "EXC"}
    write(pd.DataFrame({
        "EVENT_ID": ev.event_id, "SHIPMENT_NO": ev.shipment_id, "EVENT_CODE": ev.event_type.map(code),
        "EVENT_TS": local, "TS_BASIS": basis, "SITE_TZ": ev.site_tz, "RECEIVED_AT": ev.received_at,
    }), "portal/delivery_events.parquet")

    inv = d["inventory"]
    pack_inv = inv.part_id.map(pack)
    as_cases = (inv.storage_location_id.str.startswith("DC-")) & (inv.on_hand_qty % pack_inv == 0) & (pack_inv > 1)
    write(pd.DataFrame({
        "LGORT": inv.storage_location_id, "MATNR": inv.part_id, "SNAP_DATE": inv.snapshot_date,
        "ON_HAND": np.where(as_cases, inv.on_hand_qty // pack_inv, inv.on_hand_qty),
        "UOM": np.where(as_cases, "CS", "EA"), "ALLOCATED_EA": inv.allocated_qty,
    }), "iot/inventory_snapshots.parquet")


def main() -> int:
    rng = np.random.default_rng(SEED)
    constants = registry_constants()
    fx = build_fx(rng)
    fx_of = fx_lookup(fx)
    suppliers = build_suppliers(rng)
    parts = build_parts(rng)
    customers = build_customers(rng)
    locations = build_locations()
    tariffs = build_tariffs(parts, rng)
    combos, lines, shipments, ship_lines = build_sales(rng, customers, parts, locations, CARRIERS)
    shipments, ship_lines = price_freight(shipments, ship_lines, parts, fx_of)
    events, shipments = build_events(rng, shipments, customers, CARRIERS)
    inventory = build_inventory(rng, combos, ship_lines.merge(shipments[["shipment_id", "ship_date"]]), lines, parts)
    agreements, po_lines, inbound = build_procurement(rng, suppliers, parts, fx_of, tariffs, constants)
    truth, _, _ = compute_truth(lines, shipments, ship_lines, inventory, po_lines, customers, parts)

    world = dict(suppliers=suppliers, parts=parts, customers=customers, locations=locations,
                 tariffs=tariffs, fx=fx, agreements=agreements, po_lines=po_lines, inbound=inbound,
                 lines=lines, shipments=shipments, ship_lines=ship_lines, events=events, inventory=inventory)
    emit_sources(rng, world)
    write(build_documents(rng, events, shipments, agreements, suppliers), "content/documents.parquet")
    write(truth, "truth_metrics.parquet")

    monthly = truth[truth.grouping == "month"]
    # Inventory metrics are positions: the year's figure is its closing month, as GOVERNED_QUERY reads it.
    positions = {"days_of_inventory", "doi_units", "inventory_turns", "dio_financial", "stockout_rate"}
    headline = {metric: (g.sort_values("month").value.iloc[-1] if metric in positions
                         else g.numerator.sum() / g.denominator.sum() if g.numerator.notna().all()
                         else g.value.median())
                for metric, g in monthly.groupby("metric")}
    card = {
        "seed": SEED, "fiscal_year": f"{FY_START} to {AS_OF}", "as_of": str(AS_OF),
        "tariff_step": str(TARIFF_STEP),
        "duty_source": ("erp/material_tariffs: a per-part rate table written by this generator, with "
                        "effective_from/effective_to; the rate applied is the one in force on the inbound "
                        "shipment's depart date. reference/hts_2026.csv lists the headings that stepped and "
                        "is not read by the landed-cost model."),
        "rows": {k: len(v) for k, v in world.items()} | {"truth_metrics": len(truth)},
        "fy_headline": {k: round(float(v), 4) for k, v in headline.items()},
    }
    (OUT / "DATA_CARD.json").write_text(json.dumps(card, indent=2, sort_keys=True) + "\n")
    print(json.dumps(card, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
