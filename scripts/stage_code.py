"""PUT the committed procedure code and the loop's SQL to OPS.ARTEFACTS/code, for environments without a Git repository object.

Refuses a dirty tree for these files, so what runs in Snowflake is what is committed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

ROOT = Path(__file__).resolve().parent.parent
FILES = ("ontology/semantic.py", "ontology/metrics.yaml", "snowflake/procs/governed_query.py",
         "snowflake/procs/describe_metric.py", "snowflake/procs/explain_lineage.py",
         "snowflake/semantic/load_glossary.sql", "snowflake/policies/tags.sql")


@click.command()
@click.option("--env", default="dev", type=click.Choice(["dev", "test", "prod"]))
@click.option("--connection", default=None)
def main(env: str, connection: str | None) -> None:
    dirty = subprocess.run(["git", "status", "--porcelain", "--", *FILES], cwd=ROOT, capture_output=True, text=True).stdout
    if dirty.strip():
        raise click.ClickException(f"commit these first:\n{dirty}")
    import snowflake.connector

    db = f"SCM_{env.upper()}"
    with snowflake.connector.connect(connection_name=connection or f"scm_{env}", database=db) as conn:
        cur = conn.cursor()
        for rel in FILES:
            folder = rel.rsplit("/", 1)[0]
            cur.execute(f"PUT 'file://{(ROOT / rel).as_posix()}' @{db}.OPS.ARTEFACTS/code/{folder} "
                        "AUTO_COMPRESS = FALSE OVERWRITE = TRUE")
            click.echo(f"  {rel}")
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    click.echo(f"staged {len(FILES)} files at {sha}")


if __name__ == "__main__":
    sys.exit(main())
