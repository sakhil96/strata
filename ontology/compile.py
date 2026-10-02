"""Compile the SCM ontology and metric registry into downstream targets."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import click
import yaml

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = ROOT / "ontology" / "ontology.yaml"
METRICS_PATH = ROOT / "ontology" / "metrics.yaml"
GENERATED_DIR = ROOT / "ontology" / "generated"
SEMANTIC_DIR = ROOT / "snowflake" / "semantic"
DBT_DIR = ROOT / "dbt"
CUBE_DIR = ROOT / "cube" / "model"

HEADER = "# Generated from ontology/*.yaml by compile.py; edit the registry, not this file."

REQUIRED_METRIC_FIELDS = [
    "title", "type", "grain", "date_basis", "window",
    "numerator", "denominator", "definition", "formula_text",
    "synonyms", "variants", "owner", "steward", "scor_attribute",
    "unit", "persona_synonyms", "version", "status",
    "approved_by", "approved_on",
]

PERSONA_VIEWS = ["PLANNING_SV", "PROCUREMENT_SV", "LOGISTICS_SV", "EXECUTIVE_SV"]
PERSONA_ROLES = {
    "PLANNING_SV": "PLANNING_ROLE",
    "PROCUREMENT_SV": "PROCUREMENT_ROLE",
    "LOGISTICS_SV": "LOGISTICS_ROLE",
    "EXECUTIVE_SV": "EXECUTIVE_ROLE",
}


def load_ontology() -> dict[str, Any]:
    with open(ONTOLOGY_PATH) as f:
        return yaml.safe_load(f)


def load_metrics() -> dict[str, Any]:
    with open(METRICS_PATH) as f:
        data = yaml.safe_load(f)
    return data.get("metrics", {})


def validate_metrics(metrics: dict[str, Any], env: str) -> list[str]:
    errors = []
    for name, defn in metrics.items():
        for field in REQUIRED_METRIC_FIELDS:
            if field not in defn or defn[field] is None:
                errors.append(f"metric '{name}' missing required field '{field}'")
        if env == "prod" and defn.get("status") != "approved":
            errors.append(f"metric '{name}' has status '{defn.get('status')}', only approved metrics deploy to prod")
    return errors


def build_semantic_metric_expr(name: str, defn: dict[str, Any]) -> dict[str, Any]:
    """Build a semantic view metric definition from the registry entry."""
    return {
        "name": name,
        "title": defn["title"],
        "type": defn["type"],
        "definition": defn["definition"],
        "formula_text": defn["formula_text"],
        "grain": defn["grain"],
        "date_basis": defn["date_basis"],
        "owner": defn["owner"],
        "steward": defn["steward"],
        "version": defn["version"],
    }


def extract_sensitivity_annotations(ontology: dict[str, Any]) -> list[dict[str, str]]:
    """Extract columns with sensitivity annotations for policy generation."""
    bindings = []
    for cls_name, cls_def in ontology.get("classes", {}).items():
        for attr_name, attr_def in (cls_def.get("attributes") or {}).items():
            annotations = attr_def.get("annotations", {})
            if "sensitivity" in annotations:
                bindings.append({
                    "class": cls_name,
                    "attribute": attr_name,
                    "sensitivity": annotations["sensitivity"],
                })
    return bindings


def generate_semantic_yaml(
    ontology: dict[str, Any],
    metrics: dict[str, Any],
    env: str,
    version: int,
) -> dict[str, str]:
    """Generate semantic view YAML files. Returns {filename: content}."""
    outputs = {}

    base_metrics = []
    for name, defn in metrics.items():
        base_metrics.append(build_semantic_metric_expr(name, defn))

    governed_view = {
        "name": f"SCM_GOVERNED_V{version}",
        "database": f"SCM_{env.upper()}",
        "schema": "SEMANTIC",
        "description": "Governed semantic view covering all supply chain metrics.",
        "metrics": base_metrics,
    }

    outputs[f"scm_governed_v{version}.yaml"] = yaml.dump(
        governed_view, default_flow_style=False, sort_keys=False
    )

    for persona_view in PERSONA_VIEWS:
        role = PERSONA_ROLES[persona_view]
        role_key = role.replace("_ROLE", "_ROLE")

        persona_metrics = []
        for name, defn in metrics.items():
            metric = build_semantic_metric_expr(name, defn)
            synonyms = defn.get("persona_synonyms", {}).get(role, [])
            if synonyms:
                metric["synonyms"] = synonyms
            persona_metrics.append(metric)

        view = {
            "name": f"{persona_view}_V{version}",
            "database": f"SCM_{env.upper()}",
            "schema": "SEMANTIC",
            "description": f"Persona semantic view for {role}.",
            "metrics": persona_metrics,
        }

        outputs[f"{persona_view.lower()}_v{version}.yaml"] = yaml.dump(
            view, default_flow_style=False, sort_keys=False
        )

    return outputs


def generate_glossary(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate glossary entries from the metric registry."""
    entries = []
    for name, defn in metrics.items():
        entry = {
            "metric_name": name,
            "title": defn["title"],
            "definition": defn["definition"],
            "formula_text": defn["formula_text"],
            "owner": defn["owner"],
            "steward": defn["steward"],
            "version": defn["version"],
            "status": defn["status"],
            "scor_attribute": defn["scor_attribute"],
            "unit": defn["unit"],
            "grain": defn["grain"],
            "date_basis": defn["date_basis"],
            "synonyms": defn.get("synonyms", []),
            "variants": list((defn.get("variants") or {}).keys()),
        }
        entries.append(entry)
    return entries


def generate_deploy_sql(env: str, version: int) -> str:
    """Generate the deploy.sql for semantic views."""
    db = f"SCM_{env.upper()}"
    lines = [HEADER, "", f"USE DATABASE {db};", "USE SCHEMA SEMANTIC;", ""]

    view_files = [f"scm_governed_v{version}.yaml"] + [
        f"{pv.lower()}_v{version}.yaml" for pv in PERSONA_VIEWS
    ]

    for vf in view_files:
        view_name = vf.replace(".yaml", "").upper()
        lines.append(f"-- Deploy {view_name}")
        lines.append(
            f"SELECT SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML("
            f"'{db}.SEMANTIC.{view_name}', "
            f"$$@SEMANTIC.VIEW_YAML/{vf}$$);"
        )
        lines.append("")

    return "\n".join(lines)


def generate_versioning_sql(env: str, version: int) -> str:
    """Generate the versioning.sql that swaps grants from V{n} to V{n+1}."""
    db = f"SCM_{env.upper()}"
    lines = [HEADER, "", f"USE ROLE SECURITYADMIN;", ""]

    prev = version - 1 if version > 1 else None

    all_views = ["SCM_GOVERNED"] + PERSONA_VIEWS
    role_map = {"SCM_GOVERNED": "SCM_READER", **PERSONA_ROLES}

    for view_base in all_views:
        role = role_map[view_base]
        new_view = f"{db}.SEMANTIC.{view_base}_V{version}"
        lines.append(f"GRANT SELECT ON VIEW {new_view} TO ROLE {role};")

        if prev:
            old_view = f"{db}.SEMANTIC.{view_base}_V{prev}"
            lines.append(f"-- Keep {old_view} for rollback but revoke active grants")
            lines.append(f"REVOKE SELECT ON VIEW {old_view} FROM ROLE {role};")
        lines.append("")

    return "\n".join(lines)


def generate_dbt_schema(ontology: dict[str, Any]) -> str:
    """Generate dbt schema.yml with descriptions and basic tests."""
    models = []
    for cls_name, cls_def in ontology.get("classes", {}).items():
        columns = []
        for attr_name, attr_def in (cls_def.get("attributes") or {}).items():
            col = {
                "name": attr_name,
                "description": attr_def.get("description", ""),
            }
            tests = []
            if attr_def.get("identifier"):
                tests.extend(["unique", "not_null"])
            col["tests"] = tests
            columns.append(col)
        models.append({
            "name": cls_name.lower(),
            "description": cls_def.get("description", ""),
            "columns": columns,
        })

    schema = {"version": 2, "models": models}
    return HEADER + "\n" + yaml.dump(schema, default_flow_style=False, sort_keys=False)


def generate_ossie_model(ontology: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    """Generate an Apache Ossie semantic model."""
    datasets = []
    for cls_name, cls_def in ontology.get("classes", {}).items():
        fields = []
        for attr_name, attr_def in (cls_def.get("attributes") or {}).items():
            fields.append({
                "name": attr_name,
                "description": attr_def.get("description", ""),
                "type": "dimension" if not attr_name.endswith(("_qty", "_value", "_cost", "_charge", "_rate", "_days", "_hours")) else "measure",
            })
        datasets.append({
            "name": cls_name.lower(),
            "description": cls_def.get("description", ""),
            "fields": fields,
        })

    ossie_metrics = []
    for name, defn in metrics.items():
        ossie_metrics.append({
            "name": name,
            "title": defn["title"],
            "definition": defn["definition"],
            "formula": defn["formula_text"],
            "type": defn["type"],
        })

    return {
        "version": "1.0",
        "name": "scm_ontology",
        "description": "Supply chain ontology — Apache Ossie interchange model.",
        "datasets": datasets,
        "metrics": ossie_metrics,
    }


def generate_cube_models(ontology: dict[str, Any], metrics: dict[str, Any]) -> dict[str, str]:
    """Generate Cube.js model files for the local DuckDB fallback."""
    outputs = {}

    for cls_name, cls_def in ontology.get("classes", {}).items():
        dimensions = []
        measures = []
        for attr_name, attr_def in (cls_def.get("attributes") or {}).items():
            if attr_name.endswith(("_qty", "_value_std", "_cost", "_charge", "_rate", "_price")):
                measures.append(f"    {attr_name}: {{ sql: `{attr_name}`, type: `number` }}")
            else:
                dim_type = "time" if attr_def.get("range") in ("date", "datetime") else "string"
                dimensions.append(f"    {attr_name}: {{ sql: `{attr_name}`, type: `{dim_type}` }}")

        cube_content = f"""cube(`{cls_name}`, {{
  sql: `SELECT * FROM {cls_name.lower()}`,

  dimensions: {{
{chr(10).join(dimensions)}
  }},

  measures: {{
    count: {{ type: `count` }},
{chr(10).join(measures)}
  }}
}});
"""
        outputs[f"{cls_name}.js"] = cube_content

    return outputs


def generate_policies_sql(ontology: dict[str, Any], env: str) -> str:
    """Generate masking policy bindings from sensitivity annotations."""
    db = f"SCM_{env.upper()}"
    bindings = extract_sensitivity_annotations(ontology)
    lines = [HEADER, "", f"USE ROLE SCM_ADMIN;", f"USE DATABASE {db};", ""]

    for binding in bindings:
        table = f"{db}.CONFORMED.{binding['class'].upper()}"
        col = binding["attribute"]
        sensitivity = binding["sensitivity"]

        lines.append(f"ALTER TAG {db}.CONFORMED.SENSITIVITY SET ON COLUMN {table}.{col} = '{sensitivity}';")

        if sensitivity == "CONFIDENTIAL":
            lines.append(
                f"ALTER TABLE {table} MODIFY COLUMN {col} "
                f"SET MASKING POLICY {db}.CONFORMED.MASK_CONFIDENTIAL_STRING;"
            )
        elif sensitivity == "RESTRICTED":
            lines.append(
                f"ALTER TABLE {table} MODIFY COLUMN {col} "
                f"SET MASKING POLICY {db}.CONFORMED.MASK_RESTRICTED_NUMBER;"
            )
        lines.append("")

    return "\n".join(lines)


@click.command()
@click.option("--target", multiple=True, default=["all"],
              help="Targets: snowflake-semantic, vqr, policies, dbt, glossary, ossie, cube, databricks, all")
@click.option("--env", default="dev", type=click.Choice(["dev", "test", "prod"]))
@click.option("--version", default=1, type=int, help="Semantic view version number")
def compile_ontology(target: tuple[str, ...], env: str, version: int) -> None:
    """Compile the SCM ontology into downstream targets."""
    targets = set(target)
    if "all" in targets:
        targets = {"snowflake-semantic", "vqr", "policies", "dbt", "glossary", "ossie", "cube", "databricks"}

    ontology = load_ontology()
    metrics = load_metrics()

    errors = validate_metrics(metrics, env)
    if errors:
        for err in errors:
            click.echo(f"  {err}", err=True)
        sys.exit(1)

    click.echo(f"Compiling {len(metrics)} metrics for {env} environment, version {version}")
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    if "snowflake-semantic" in targets:
        SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)
        yamls = generate_semantic_yaml(ontology, metrics, env, version)
        for filename, content in yamls.items():
            out_path = SEMANTIC_DIR / filename
            out_path.write_text(HEADER + "\n" + content)
            click.echo(f"  wrote {out_path.relative_to(ROOT)}")

        deploy_sql = generate_deploy_sql(env, version)
        deploy_path = SEMANTIC_DIR / "deploy.sql"
        deploy_path.write_text(deploy_sql)
        click.echo(f"  wrote {deploy_path.relative_to(ROOT)}")

        versioning_sql = generate_versioning_sql(env, version)
        versioning_path = SEMANTIC_DIR / "versioning.sql"
        versioning_path.write_text(versioning_sql)
        click.echo(f"  wrote {versioning_path.relative_to(ROOT)}")

    if "policies" in targets:
        policies_sql = generate_policies_sql(ontology, env)
        policies_path = SEMANTIC_DIR / "policies.sql"
        policies_path.write_text(policies_sql)
        click.echo(f"  wrote {policies_path.relative_to(ROOT)}")

    if "dbt" in targets:
        schema_yml = generate_dbt_schema(ontology)
        schema_path = DBT_DIR / "models" / "conformed" / "schema.yml"
        schema_path.parent.mkdir(parents=True, exist_ok=True)
        schema_path.write_text(schema_yml)
        click.echo(f"  wrote {schema_path.relative_to(ROOT)}")

    if "glossary" in targets:
        glossary = generate_glossary(metrics)
        glossary_path = GENERATED_DIR / "glossary.json"
        glossary_path.write_text(json.dumps(glossary, indent=2))
        click.echo(f"  wrote {glossary_path.relative_to(ROOT)}")

    if "ossie" in targets:
        ossie = generate_ossie_model(ontology, metrics)
        ossie_path = GENERATED_DIR / "ossie_model.yaml"
        ossie_path.write_text(HEADER + "\n" + yaml.dump(ossie, default_flow_style=False, sort_keys=False))
        click.echo(f"  wrote {ossie_path.relative_to(ROOT)}")

    if "cube" in targets:
        CUBE_DIR.mkdir(parents=True, exist_ok=True)
        cubes = generate_cube_models(ontology, metrics)
        for filename, content in cubes.items():
            out_path = CUBE_DIR / filename
            out_path.write_text(content)
        click.echo(f"  wrote {len(cubes)} Cube models to {CUBE_DIR.relative_to(ROOT)}/")

    click.echo("Compilation complete.")


if __name__ == "__main__":
    compile_ontology()
