"""Deploy the compiled semantic views and prove each one round-trips.

For every view: validate the YAML without creating anything, create it, read the YAML back from
Snowflake and compare the parts the compiler owns (tables, dimensions, facts, metrics and their
expressions, relationships, verified queries). Snowflake adds defaults, reorders keys and upper-cases
verified-query names, so the comparison is on those parts, case-folded, not on text.
"""

from __future__ import annotations

import sys
from pathlib import Path

import click
import yaml

ROOT = Path(__file__).resolve().parent.parent
SEMANTIC = ROOT / "snowflake" / "semantic"


def signature(model: dict) -> dict:
    def names(items, *keys):
        return sorted(tuple(str(i.get(k, "")).strip().lower() for k in keys) for i in items or [])

    tables = {}
    for t in model.get("tables", []):
        tables[t["name"].lower()] = {
            "base": tuple(t["base_table"][k].upper() for k in ("database", "schema", "table")),
            "dimensions": names(t.get("dimensions"), "name", "expr"),
            "time_dimensions": names(t.get("time_dimensions"), "name", "expr"),
            "facts": names(t.get("facts"), "name", "expr"),
            "metrics": names(t.get("metrics"), "name", "expr"),
        }
    return {
        "tables": tables,
        "relationships": names(model.get("relationships"), "name"),
        "verified_queries": sorted(q["name"].lower() for q in model.get("verified_queries") or []),
    }


@click.command()
@click.option("--env", default="dev", type=click.Choice(["dev", "test", "prod"]))
@click.option("--connection", default=None)
@click.option("--version", "version", default=1, type=int)
@click.option("--check-only", is_flag=True, help="Compare the deployed views with the compiled YAML; create nothing.")
def main(env: str, connection: str | None, version: int, check_only: bool) -> None:
    import snowflake.connector

    db = f"SCM_{env.upper()}"
    files = sorted(SEMANTIC.glob(f"*_v{version}.yaml"))
    if not files:
        raise click.ClickException(f"no compiled views for V{version}; run make compile")
    failed = 0
    with snowflake.connector.connect(connection_name=connection or f"scm_{env}", database=db, schema="SEMANTIC") as conn:
        cur = conn.cursor()
        for path in files:
            text = path.read_text()
            name = yaml.safe_load(text)["name"]
            if not check_only:
                cur.execute("CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(%s, %s, TRUE)", (f"{db}.SEMANTIC", text))
                cur.execute("CALL SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML(%s, %s)", (f"{db}.SEMANTIC", text))
            cur.execute("SELECT SYSTEM$READ_YAML_FROM_SEMANTIC_VIEW(%s)", (f"{db}.SEMANTIC.{name}",))
            back = yaml.safe_load(cur.fetchone()[0])
            same = signature(yaml.safe_load(text)) == signature(back)
            failed += not same
            click.echo(f"{'round-trip ok ' if same else 'ROUND-TRIP DIFF'}  {db}.SEMANTIC.{name}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
