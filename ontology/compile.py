"""Compile the ontology and metric registry into every downstream target."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import semantic

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = ROOT / "ontology" / "ontology.yaml"
GENERATED = ROOT / "ontology" / "generated"
SEMANTIC_DIR = ROOT / "snowflake" / "semantic"
DBT_SCHEMA = ROOT / "dbt" / "models" / "conformed" / "schema.yml"
CUBE_DIR = ROOT / "cube" / "model"
DATABRICKS_DIR = ROOT / "ontology" / "generated" / "databricks"
QUESTIONS = ROOT / "eval" / "questions.yaml"

HEADER = "Generated from ontology/*.yaml by compile.py; edit the registry, not this file."
TARGETS = ("snowflake-semantic", "vqr", "policies", "dbt", "glossary", "ossie", "cube", "databricks", "linkml", "er")
LINKML = (("gen-pydantic", "scm_ontology_pydantic.py"), ("gen-json-schema", "scm_ontology.schema.json"),
          ("gen-owl", "scm_ontology.owl.nt"), ("gen-erdiagram", "er_diagram.md"))
ER_ROWS = (("Supplier", "SupplierPartAgreement", "Part", "TariffCode"),
           ("PurchaseOrderLine", "GoodsReceipt", "Plant", "StorageLocation", "InventorySnapshot"),
           ("Customer", "SalesOrderLine", "ShipmentLine", "Shipment", "Carrier"),
           ("Lane", "DeliveryEvent", "FxRate"))
VIEWS = {
    "SCM_GOVERNED": None,
    "PLANNING_SV": "PLANNING_ROLE",
    "PROCUREMENT_SV": "PROCUREMENT_ROLE",
    "LOGISTICS_SV": "LOGISTICS_ROLE",
    "EXECUTIVE_SV": "EXECUTIVE_ROLE",
}
VIEW_GRANTEE = {"SCM_GOVERNED": "SCM_READER", **{v: r for v, r in VIEWS.items() if r}}
PERSONA_FOCUS = {
    None: "Answer for any role. Prefer the governed default metric unless the question names a variant.",
    "PLANNING_ROLE": "Planners think in plants, families and months; default to plant_id and period_month.",
    "PROCUREMENT_ROLE": "Buyers think in suppliers and receipts; offer supplier_name when it is reachable.",
    "LOGISTICS_ROLE": "Logistics thinks in carriers and lanes; offer carrier_name when it is reachable.",
    "EXECUTIVE_ROLE": "Executives want the headline for the fiscal year and the trend by month.",
}
FACT_TYPES = {"transit_hours_elapsed": "NUMBER(18,4)", "cycle_days": "NUMBER(9,0)", "lead_days": "NUMBER(9,0)"}
ROW_POLICY_MODELS = ("FCT_SALES_ORDER_LINE", "FCT_SHIPMENT", "FCT_SHIPMENT_LINE", "FCT_PO_LINE", "FCT_INVENTORY_MONTH")
DBT_RELATIONSHIPS = (
    ("fct_sales_order_line", "customer_id", "dim_customer", "customer_id"),
    ("fct_sales_order_line", "part_id", "dim_part", "part_id"),
    ("fct_sales_order_line", "plant_id", "dim_plant", "plant_id"),
    ("fct_po_line", "supplier_id", "dim_supplier", "supplier_id"),
    ("fct_po_line", "part_id", "dim_part", "part_id"),
    ("fct_shipment", "carrier_id", "dim_carrier", "carrier_id"),
    ("fct_shipment_line", "shipment_id", "fct_shipment", "shipment_id"),
    ("fct_receipt", "po_line_id", "fct_po_line", "po_line_id"),
    ("fct_delivery_event", "shipment_id", "fct_shipment", "shipment_id"),
)
DBT_ACCEPTED = (
    ("fct_delivery_event", "event_type", ["picked_up", "departed", "arrived", "delivered", "exception"]),
    ("dim_plant", "region", ["US", "EMEA", "APAC"]),
    ("dim_customer", "segment", ["Industrial", "Retail", "Government", "Healthcare"]),
)
CLASS_MODEL = {
    "Supplier": "dim_supplier", "Part": "dim_part", "Plant": "dim_plant", "StorageLocation": "dim_storage_location",
    "Customer": "dim_customer", "Carrier": "dim_carrier", "TariffCode": "dim_tariff_code",
    "PurchaseOrderLine": "fct_po_line", "GoodsReceipt": "fct_receipt", "SalesOrderLine": "fct_sales_order_line",
    "Shipment": "fct_shipment", "ShipmentLine": "fct_shipment_line", "DeliveryEvent": "fct_delivery_event",
    "InventorySnapshot": "fct_inventory_snapshot", "FxRate": "fct_fx_rate",
}


def dump(data: Any) -> str:
    return f"# {HEADER}\n" + yaml.safe_dump(data, sort_keys=False, width=110, allow_unicode=True)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    click.echo(f"  wrote {path.relative_to(ROOT)}")


def approved_epoch(metric: dict[str, Any]) -> int:
    day = datetime.strptime(str(metric["approved_on"]), "%Y-%m-%d").replace(tzinfo=UTC)
    return int(day.timestamp())


def tag(db: str, name: str, value: Any) -> dict[str, Any]:
    return {"name": {"database": db, "schema": "CONFORMED", "tag": name}, "value": str(value)}


def check_registry(registry: semantic.Registry, env: str) -> list[str]:
    problems = []
    for name, metric in registry.metrics.items():
        table = metric["semantic"]["table"]
        if table not in registry.tables:
            problems.append(f"{name}: unknown logical table {table}")
        if f"{table}." not in metric["semantic"]["expr"]:
            problems.append(f"{name}: expression must reference {table}.<fact>")
        # Snowflake resolves a column name to a same-named metric first, so a fact named like a
        # metric on its table makes the semantic view cyclic.
        if table in registry.tables and name in registry.tables[table].get("facts", []):
            problems.append(f"{name}: a fact on {table} has the metric's name")
        if env == "prod" and metric["status"] != "approved":
            problems.append(f"{name}: status {metric['status']} cannot ship to SCM_PROD")
    return problems


def semantic_view(registry: semantic.Registry, view: str, persona: str | None, env: str, version: int,
                  verified: list[dict[str, Any]]) -> dict[str, Any]:
    db = f"SCM_{env.upper()}"
    tables = []
    for name, spec in registry.tables.items():
        logical: dict[str, Any] = {
            "name": name,
            "description": spec["description"],
            "base_table": {"database": db, "schema": "CONFORMED", "table": spec["base_table"]},
            "primary_key": {"columns": list(spec["primary_key"])},
        }
        dims = []
        for key in sorted(spec.get("keys", {})):
            dims.append({"name": key, "expr": key, "data_type": "VARCHAR"})
        for dim, meta in spec.get("dimensions", {}).items():
            if dim in spec["primary_key"]:
                dims = [d for d in dims if d["name"] != dim]
            dims.append({"name": dim, "synonyms": list(meta.get("synonyms", [])), "expr": dim, "data_type": "VARCHAR"})
        for pk in spec["primary_key"]:
            if pk not in {d["name"] for d in dims} and pk != spec.get("period"):
                dims.append({"name": pk, "expr": pk, "data_type": "VARCHAR"})
        if dims:
            logical["dimensions"] = dims
        if "period" in spec:
            logical["time_dimensions"] = [{
                "name": semantic.PERIOD,
                "synonyms": ["month", "period"],
                "description": f"First day of the month of {spec['period'].replace('_month', '')} for this table.",
                "expr": spec["period"],
                "data_type": "DATE",
            }]
        if spec.get("facts"):
            logical["facts"] = [{"name": f, "expr": f, "data_type": FACT_TYPES.get(f, "NUMBER(38,6)"),
                                 "access_modifier": "private_access"} for f in spec["facts"]]
        metrics = []
        for mname, m in registry.metrics.items():
            if m["semantic"]["table"] != name:
                continue
            synonyms = list(m["synonyms"])
            if persona:
                synonyms += [s for s in m["persona_synonyms"].get(persona, []) if s not in synonyms]
            entry: dict[str, Any] = {
                "name": mname,
                "synonyms": synonyms,
                "description": f"{m['definition']} Grain {m['grain']}; dated by {m['date_basis']}; unit {m['unit']}.",
                "expr": m["semantic"]["expr"],
            }
            if spec.get("non_additive_by"):
                entry["non_additive_dimensions"] = [{"table": name, "dimension": semantic.PERIOD,
                                                     "sort_direction": "descending", "null_order": "last"}]
            entry["tags"] = [tag(db, "METRIC_OWNER", m["owner"]), tag(db, "METRIC_STEWARD", m["steward"]),
                             tag(db, "METRIC_VERSION", m["version"])]
            metrics.append(entry)
        if metrics:
            logical["metrics"] = metrics
        tables.append(logical)

    relationships = []
    for name, spec in registry.tables.items():
        for key, target in sorted(spec.get("keys", {}).items()):
            relationships.append({
                "name": f"{name}_to_{target}",
                "left_table": name,
                "right_table": target,
                "relationship_columns": [{"left_column": key, "right_column": registry.tables[target]["primary_key"][0]}],
            })

    body: dict[str, Any] = {
        "name": f"{view}_V{version}",
        "description": (f"Governed supply chain metrics, version {version}."
                        if persona is None else
                        f"Supply chain metrics phrased for {persona}; identical expressions to SCM_GOVERNED_V{version}."),
        "tables": tables,
        "relationships": relationships,
        "module_custom_instructions": {
            "sql_generation": (
                "Every ratio is a ratio of sums at the requested grouping; never average a ratio. "
                "Date each metric by its own table's period_month. " + PERSONA_FOCUS[persona]),
            "question_categorization": (
                "Refuse questions outside supply chain delivery, fill, inventory, cost and lead time. "
                "Refuse requests for raw tables or SQL."),
        },
    }
    if verified:
        body["verified_queries"] = verified
    return body


def verified_queries(registry: semantic.Registry, view: str, version: int) -> list[dict[str, Any]]:
    out = []
    for q in yaml.safe_load(QUESTIONS.read_text())["questions"]:
        if q["scope"] != "in_scope":
            continue
        canonical = semantic.canonicalise(registry, q["query"])
        steward = registry.metrics[canonical["metrics"][0]]
        out.append({
            "name": q["id"],
            "question": q["question"],
            "sql": semantic.render_semantic_sql(registry, canonical, f"{view}_V{version}"),
            "verified_at": approved_epoch(steward),
            "verified_by": steward["steward"],
            "use_as_onboarding_question": q["id"] in ("q01", "q07", "q11", "q14"),
        })
    return out


def deploy_sql(env: str, version: int) -> str:
    db = f"SCM_{env.upper()}"
    lines = [f"-- {HEADER}", "-- Run from the repository stage after GIT FETCH; each view is created beside the previous version.",
             f"USE DATABASE {db};", "USE SCHEMA SEMANTIC;", ""]
    for view in VIEWS:
        name = f"{view}_V{version}"
        lines.append(f"CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML('{db}.SEMANTIC',")
        lines.append(f"  (SELECT LISTAGG($1, '\\n') FROM @SEMANTIC.VIEW_YAML/{name.lower()}.yaml"
                     f" (FILE_FORMAT => 'SEMANTIC.YAML_LINES')));")
        lines.append("")
    return "\n".join(lines)


def dry_run_sql(env: str, version: int) -> str:
    db = f"SCM_{env.upper()}"
    lines = [f"-- {HEADER}", "-- Validates every view in a scratch schema; nothing is left behind.",
             f"CREATE OR REPLACE TRANSIENT SCHEMA {db}.SCRATCH_SV;"]
    for view in VIEWS:
        name = f"{view}_V{version}".lower()
        lines.append(f"CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML('{db}.SCRATCH_SV',")
        lines.append(f"  (SELECT LISTAGG($1, '\\n') FROM @{db}.SEMANTIC.VIEW_YAML/{name}.yaml"
                     f" (FILE_FORMAT => '{db}.SEMANTIC.YAML_LINES')), TRUE);")
    lines.append(f"DROP SCHEMA {db}.SCRATCH_SV;")
    return "\n".join(lines) + "\n"


def versioning_sql(env: str, version: int) -> str:
    db = f"SCM_{env.upper()}"
    lines = [f"-- {HEADER}",
             f"-- Promote V{version}. Rollback is this file compiled with --version {version - 1}.",
             "USE ROLE SCM_ADMIN;", ""]
    for view, role in VIEW_GRANTEE.items():
        lines.append(f"GRANT SELECT ON SEMANTIC VIEW {db}.SEMANTIC.{view}_V{version} TO ROLE {role};")
        for older in range(1, version):
            lines.append(f"REVOKE SELECT ON SEMANTIC VIEW {db}.SEMANTIC.{view}_V{older} FROM ROLE {role};")
    lines.append("")
    lines.append(f"UPDATE {db}.SEMANTIC.ACTIVE_VERSION SET version = {version}, promoted_at = CURRENT_TIMESTAMP();")
    return "\n".join(lines) + "\n"


def policies_sql(ontology: dict[str, Any], env: str) -> str:
    db = f"SCM_{env.upper()}"
    lines = [f"-- {HEADER}",
             "-- Masking is tag-based: 04_policies.sql attaches one string and one number policy to the",
             "-- SENSITIVITY tag, and each policy reads the tag value. Tagging a column is the whole binding.",
             "USE ROLE SCM_ADMIN;", ""]
    for cls, spec in ontology["classes"].items():
        model = CLASS_MODEL.get(cls)
        for attr, meta in (spec.get("attributes") or {}).items():
            level = (meta.get("annotations") or {}).get("sensitivity")
            if level and model:
                lines.append(f"ALTER TABLE {db}.CONFORMED.{model.upper()} MODIFY COLUMN {attr} "
                             f"SET TAG {db}.CONFORMED.SENSITIVITY = '{level}';")
    lines.append("")
    lines.append("-- Persona roles see the plants USER_PLANT_SCOPE grants them; admin and executive see all.")
    lines.append("-- Row access is Enterprise edition; render_sql.py drops the block on Standard.")
    lines.append("-- @enterprise")
    for model in ROW_POLICY_MODELS:
        lines.append(f"ALTER TABLE {db}.CONFORMED.{model} DROP ALL ROW ACCESS POLICIES;")
        lines.append(f"ALTER TABLE {db}.CONFORMED.{model} ADD ROW ACCESS POLICY {db}.CONFORMED.PLANT_ACCESS ON (plant_id);")
    lines.append("-- @end")
    return "\n".join(lines) + "\n"


def dbt_schema(ontology: dict[str, Any], registry: semantic.Registry) -> str:
    models = {}
    for cls, model in CLASS_MODEL.items():
        spec = ontology["classes"][cls]
        columns = [{"name": attr, "description": meta.get("description", ""), "data_tests": ["unique", "not_null"]}
                   for attr, meta in (spec.get("attributes") or {}).items() if meta.get("identifier")]
        models[model] = {"name": model, "description": spec.get("description", ""), "columns": columns}
    for model, column, target, field in DBT_RELATIONSHIPS:
        models[model]["columns"].append({
            "name": column, "data_tests": ["not_null", {"relationships": {"to": f"ref('{target}')", "field": field}}]})
    for model, column, values in DBT_ACCEPTED:
        models[model]["columns"].append({"name": column, "data_tests": [{"accepted_values": {"values": values}}]})
    models["fct_inventory_month"] = {
        "name": "fct_inventory_month", "description": "Month-end inventory position per storage location and part.",
        "columns": [{"name": c, "data_tests": ["not_null"]} for c in ("snapshot_month", "plant_id", "on_hand_value_end")]}
    missing = {t["base_table"].lower() for t in registry.tables.values()} - set(models)
    if missing:
        raise click.ClickException(f"semantic tables without a dbt model: {sorted(missing)}")
    return dump({"version": 2, "models": list(models.values())})


def glossary(registry: semantic.Registry) -> list[dict[str, Any]]:
    entries = []
    for name, m in sorted(registry.metrics.items()):
        table = m["semantic"]["table"]
        base = registry.tables[table]["base_table"]
        entries.append({
            "metric_name": name, "title": m["title"], "parent": m["parent"], "variants": m["variants"],
            "type": m["type"], "grain": m["grain"], "date_basis": m["date_basis"], "window": m["window"],
            "numerator": m["numerator"], "denominator": m["denominator"], "definition": m["definition"],
            "formula_text": m["formula_text"], "expression": m["semantic"]["expr"], "unit": m["unit"],
            "owner": m["owner"], "steward": m["steward"], "scor_attribute": m["scor_attribute"],
            "synonyms": m["synonyms"], "persona_synonyms": m["persona_synonyms"], "version": m["version"],
            "status": m["status"], "approved_by": m["approved_by"], "approved_on": str(m["approved_on"]),
            "deprecated_by": m.get("deprecated_by"),
            "lineage": {"semantic_table": table, "conformed_model": base.lower(),
                        "facts": sorted({f for f in registry.tables[table].get("facts", []) if f in m["semantic"]["expr"]})},
        })
    return entries


def glossary_load_sql(env: str) -> str:
    db = f"SCM_{env.upper()}"
    return "\n".join([
        f"-- {HEADER}",
        f"USE SCHEMA {db}.SEMANTIC;",
        f"CREATE TABLE IF NOT EXISTS {db}.SEMANTIC.GLOSSARY (metric_name STRING, entry VARIANT, loaded_at TIMESTAMP_NTZ);",
        "CREATE OR REPLACE TEMPORARY TABLE glossary_incoming AS",
        "  SELECT value:metric_name::STRING AS metric_name, value AS entry",
        f"  FROM @{db}.SEMANTIC.VIEW_YAML/glossary.json (FILE_FORMAT => '{db}.SEMANTIC.JSON_DOC'),",
        "  LATERAL FLATTEN(input => $1);",
        f"MERGE INTO {db}.SEMANTIC.GLOSSARY g USING glossary_incoming i ON g.metric_name = i.metric_name",
        "  WHEN MATCHED THEN UPDATE SET entry = i.entry, loaded_at = CURRENT_TIMESTAMP()",
        "  WHEN NOT MATCHED THEN INSERT VALUES (i.metric_name, i.entry, CURRENT_TIMESTAMP());", ""])


def expr(text: str) -> dict[str, Any]:
    return {"dialects": [{"dialect": "ANSI_SQL", "expression": text}]}


def ossie(registry: semantic.Registry, env: str) -> dict[str, Any]:
    db = f"SCM_{env.upper()}"
    datasets = []
    for name, spec in registry.tables.items():
        fields = [{"name": k, "expression": expr(k), "dimension": {"is_time": False}} for k in sorted(spec.get("keys", {}))]
        fields += [{"name": d, "expression": expr(d), "dimension": {"is_time": False},
                    "ai_context": {"synonyms": list(meta.get("synonyms", []))}}
                   for d, meta in spec.get("dimensions", {}).items()]
        if "period" in spec:
            fields.append({"name": semantic.PERIOD, "expression": expr(spec["period"]), "dimension": {"is_time": True}})
        fields += [{"name": f, "expression": expr(f)} for f in spec.get("facts", [])]
        datasets.append({"name": name, "source": f"{db}.CONFORMED.{spec['base_table']}",
                         "primary_key": list(spec["primary_key"]), "description": spec["description"],
                         "fields": fields})
    relationships = [{"name": f"{n}_to_{t}", "from": n, "to": t, "from_columns": [k],
                      "to_columns": [registry.tables[t]["primary_key"][0]]}
                     for n, spec in registry.tables.items() for k, t in sorted(spec.get("keys", {}).items())]
    metrics = [{"name": n, "expression": expr(m["semantic"]["expr"]), "description": m["definition"],
                "ai_context": {"synonyms": m["synonyms"], "instructions": m["formula_text"]},
                "custom_extensions": [{"vendor_name": "SNOWFLAKE", "data": json.dumps(
                    {"owner": m["owner"], "steward": m["steward"], "version": m["version"], "status": m["status"]},
                    sort_keys=True)}]}
               for n, m in sorted(registry.metrics.items())]
    return {"version": "0.2.0.dev0", "name": "scm_ontology",
            "description": "Supply chain ontology: delivery, fill, inventory, landed cost and lead time.",
            "ai_context": {"instructions": "Every ratio is a ratio of sums at the requested grouping."},
            "datasets": datasets, "relationships": relationships, "metrics": metrics}


def cube_models(registry: semantic.Registry) -> dict[str, str]:
    files = {}
    cubes = []
    for name, spec in registry.tables.items():
        dims = [{"name": spec["primary_key"][0] if len(spec["primary_key"]) == 1 else "row_key",
                 "sql": spec["primary_key"][0] if len(spec["primary_key"]) == 1
                 else " || '|' || ".join(f"CAST({c} AS VARCHAR)" for c in spec["primary_key"]),
                 "type": "string", "primary_key": True}]
        dims += [{"name": d, "sql": d, "type": "string"} for d in spec.get("dimensions", {}) if d not in spec["primary_key"]]
        dims += [{"name": k, "sql": k, "type": "string"} for k in sorted(spec.get("keys", {})) if k not in spec["primary_key"]]
        if "period" in spec:
            dims.append({"name": semantic.PERIOD, "sql": spec["period"], "type": "time"})
        measures = [{"name": m, "sql": registry.metrics[m]["semantic"]["expr"].replace(f"{name}.", "{CUBE}."),
                     "type": "number", "description": registry.metrics[m]["definition"]}
                    for m in sorted(registry.metrics) if registry.metrics[m]["semantic"]["table"] == name]
        joins = [{"name": t, "sql": f"{{CUBE}}.{k} = {{{t}}}.{registry.tables[t]['primary_key'][0]}",
                  "relationship": "many_to_one"} for k, t in sorted(spec.get("keys", {}).items())]
        cube: dict[str, Any] = {"name": name, "sql_table": f"CONFORMED.{spec['base_table']}", "dimensions": dims}
        if measures:
            cube["measures"] = measures
        if joins:
            cube["joins"] = joins
        cubes.append(cube)
    files["cubes.yml"] = dump({"cubes": cubes})
    views = []
    for view, persona in VIEWS.items():
        if persona is None:
            continue
        includes = [{"join_path": t, "includes": "*"} for t, s in registry.tables.items() if "period" in s]
        views.append({"name": view.lower(), "description": f"Persona view for {persona}.", "cubes": includes})
    files["views.yml"] = dump({"views": views})
    return files


def databricks_views(registry: semantic.Registry, env: str) -> dict[str, str]:
    files = {}
    for name, spec in registry.tables.items():
        measures = [{"name": m, "expr": registry.metrics[m]["semantic"]["expr"].replace(f"{name}.", "source.")}
                    for m in sorted(registry.metrics) if registry.metrics[m]["semantic"]["table"] == name]
        if not measures:
            continue
        joins = [{"name": t, "source": f"scm_{env}.conformed.{registry.tables[t]['base_table'].lower()}",
                  "on": f"source.{k} = {t}.{registry.tables[t]['primary_key'][0]}"}
                 for k, t in sorted(spec.get("keys", {}).items())]
        dims = [{"name": semantic.PERIOD, "expr": f"source.{spec['period']}"}]
        dims += [{"name": d, "expr": f"{t}.{d}"} for t in sorted(set(spec.get("keys", {}).values()))
                 for d in registry.tables[t].get("dimensions", {})]
        files[f"{name}.yaml"] = dump({"version": 0.1,
                                      "source": f"scm_{env}.conformed.{spec['base_table'].lower()}",
                                      "joins": joins, "dimensions": dims, "measures": measures})
    return files


def er_svg(ontology: dict[str, Any]) -> str:
    box_w, box_h, gap_x, gap_y, pad = 200, 36, 64, 72, 24
    place = {}
    for r, row in enumerate(ER_ROWS):
        for c, cls in enumerate(row):
            place[cls] = (pad + c * (box_w + gap_x), pad + 24 + r * (box_h + gap_y))
    width = pad * 2 + max(len(r) for r in ER_ROWS) * (box_w + gap_x) - gap_x
    height = pad * 2 + 24 + len(ER_ROWS) * (box_h + gap_y) - gap_y
    edges = sorted({(cls, meta["range"]) for cls, spec in ontology["classes"].items()
                    for meta in (spec.get("attributes") or {}).values()
                    if meta.get("range") in ontology["classes"] and meta["range"] != cls})
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
           'role="img" aria-labelledby="er-title" font-family="JetBrains Mono, monospace">',
           f'<title id="er-title">Entities of the supply chain ontology and the references between them. {HEADER}</title>',
           f'<rect width="{width}" height="{height}" fill="#0B0D10"/>',
           f'<text x="{pad}" y="{pad + 4}" fill="#9AA0A6" font-size="11" letter-spacing="1.5">SUPPLY CHAIN ONTOLOGY · '
           f'{len(ontology["classes"])} ENTITIES · {len(edges)} REFERENCES</text>']
    for src, dst in edges:
        (x1, y1), (x2, y2) = place[src], place[dst]
        a = (x1 + box_w / 2, y1 + box_h / 2)
        b = (x2 + box_w / 2, y2 + box_h / 2)
        mid = (a[1] + b[1]) / 2
        out.append(f'<path d="M{a[0]:.0f} {a[1]:.0f} C{a[0]:.0f} {mid:.0f}, {b[0]:.0f} {mid:.0f}, {b[0]:.0f} {b[1]:.0f}" '
                   'fill="none" stroke="#232830" stroke-width="1"/>')
    for cls, (x, y) in place.items():
        keys = sum(1 for m in (ontology["classes"][cls].get("attributes") or {}).values()
                   if m.get("range") in ontology["classes"])
        out.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" fill="#121519" stroke="#232830"/>')
        out.append(f'<text x="{x + 12}" y="{y + 22}" fill="#E9E4DA" font-size="13">{cls}</text>')
        out.append(f'<text x="{x + box_w - 12}" y="{y + 22}" fill="#9AA0A6" font-size="11" text-anchor="end">{keys}→</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def canonical_owl(turtle: str) -> str:
    """Blank-node labels differ per run; canonicalise them and sort the triples."""
    from rdflib import Graph
    from rdflib.compare import to_canonical_graph

    graph = to_canonical_graph(Graph().parse(data=turtle, format="turtle"))
    return "\n".join(sorted(line for line in graph.serialize(format="nt").splitlines() if line)) + "\n"


@click.command()
@click.option("--target", "targets", multiple=True, type=click.Choice([*TARGETS, "all"]), default=["all"])
@click.option("--env", default="dev", type=click.Choice(["dev", "test", "prod"]))
@click.option("--version", default=1, type=int, help="Semantic view version suffix.")
def main(targets: tuple[str, ...], env: str, version: int) -> None:
    chosen = set(TARGETS) if "all" in targets else set(targets)
    try:
        registry = semantic.load_registry()
    except semantic.SemanticError as exc:
        raise click.ClickException(str(exc)) from exc
    problems = check_registry(registry, env)
    if problems:
        raise click.ClickException("registry rejected:\n  " + "\n  ".join(problems))
    ontology = yaml.safe_load(ONTOLOGY_PATH.read_text())
    click.echo(f"compiling {len(registry.metrics)} metrics and variants for SCM_{env.upper()} at V{version}")

    if chosen & {"snowflake-semantic", "vqr"}:
        for view, persona in VIEWS.items():
            vqrs = verified_queries(registry, view, version) if "vqr" in chosen else []
            body = semantic_view(registry, view, persona, env, version, vqrs)
            write(SEMANTIC_DIR / f"{view.lower()}_v{version}.yaml", dump(body))
        write(SEMANTIC_DIR / "deploy.sql", deploy_sql(env, version))
        write(SEMANTIC_DIR / "dry_run.sql", dry_run_sql(env, version))
        write(SEMANTIC_DIR / "versioning.sql", versioning_sql(env, version))
    if "policies" in chosen:
        write(SEMANTIC_DIR / "policies.sql", policies_sql(ontology, env))
    if "dbt" in chosen:
        write(DBT_SCHEMA, dbt_schema(ontology, registry))
    if "glossary" in chosen:
        write(GENERATED / "glossary.json", json.dumps(glossary(registry), indent=2, sort_keys=True) + "\n")
        write(SEMANTIC_DIR / "load_glossary.sql", glossary_load_sql(env))
    if "ossie" in chosen:
        write(GENERATED / "ossie_model.yaml", dump(ossie(registry, env)))
    if "cube" in chosen:
        for f in CUBE_DIR.glob("*"):
            f.unlink()
        for fname, text in cube_models(registry).items():
            write(CUBE_DIR / fname, text)
    if "linkml" in chosen:
        import shutil
        import subprocess

        target = GENERATED / "linkml"
        target.mkdir(parents=True, exist_ok=True)
        for tool, name in LINKML:
            done = subprocess.run([tool, str(ONTOLOGY_PATH)], capture_output=True, text=True, check=True)
            write(target / name, canonical_owl(done.stdout) if tool == "gen-owl" else done.stdout)
        shutil.rmtree(target / "docs", ignore_errors=True)
        subprocess.run(["gen-doc", "-d", str(target / "docs"), str(ONTOLOGY_PATH)], capture_output=True, check=True)
        click.echo(f"  wrote {(target / 'docs').relative_to(ROOT)}/")
    if "er" in chosen:
        svg = er_svg(ontology)
        write(ROOT / "docs" / "er_diagram.svg", svg)
        write(ROOT / "web" / "public" / "er_diagram.svg", svg)
    if "databricks" in chosen:
        for fname, text in databricks_views(registry, env).items():
            write(DATABRICKS_DIR / fname, text)


if __name__ == "__main__":
    main()
