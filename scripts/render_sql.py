"""Render an environment's SQL from the committed templates and run it with the Snowflake CLI.

Templates use {{DB}}, {{ENV}}, {{WH}} and the environment's sizing keys. Blocks between
`-- @enterprise` and `-- @end` are dropped for a Standard-edition environment. Rendered files land in .strata/sql/<env>/ so what ran
can be read back; nothing is typed into Snowsight.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import click
import yaml

ROOT = Path(__file__).resolve().parent.parent
GROUPS = {
    "setup": ["snowflake/setup/0*.sql", "snowflake/setup/10_ops.sql"],
    "repo": ["snowflake/git_repo.sql", "snowflake/dbt_project.sql"],
    "objects": ["snowflake/dynamic_tables/*.sql", "snowflake/procs/create_procs.sql", "snowflake/search/*.sql",
                "snowflake/semantic/load_glossary.sql"],
    "views": ["snowflake/semantic/deploy.sql", "snowflake/semantic/policies.sql"],
    "promote": ["snowflake/semantic/versioning.sql"],
    "agent": ["snowflake/agent/create_agent.sql", "snowflake/agent/create_steward_agent.sql"],
    "loop": ["snowflake/tasks/operational_loop.sql"],
    "service": ["snowflake/spcs/compute_pool.sql", "snowflake/spcs/deploy.sql"],
}


def render(path: Path, env: str) -> str:
    settings = yaml.safe_load((ROOT / "snowflake" / "environments" / f"{env}.yaml").read_text())
    text = path.read_text()
    if settings.get("edition", "enterprise") == "standard":
        text = re.sub(r"^-- @enterprise\n.*?^-- @end\n", "", text, flags=re.S | re.M)
    else:
        text = re.sub(r"^-- @(enterprise|end)\n", "", text, flags=re.M)
    tokens = {
        "DB_LOWER": settings["database"].lower(), "DB": settings["database"], "ENV_UPPER": env.upper(),
        "ENV": env.upper(), "WH": settings["warehouse"], "WH_SIZE": settings["warehouse_size"],
        "AUTO_SUSPEND": str(settings["auto_suspend_secs"]), "RETENTION": str(settings["retention_days"]),
        "LONG_RETENTION": str(settings["long_retention_days"]), "MONITOR_QUOTA": str(settings["monitor_credit_quota"]),
        "ALERT_EMAIL": os.environ.get("STRATA_ALERT_EMAIL", ""),
        "ORIGIN_CIDR": os.environ.get("STRATA_ORIGIN_CIDR", ""),
        "SLO_ALERT_SCHEDULE": settings.get("slo_alert_schedule", "15 MINUTE"),
    }
    for key, value in tokens.items():
        text = text.replace("{{" + key + "}}", value)
    if "{{ALERT_EMAIL}}" in path.read_text() and not tokens["ALERT_EMAIL"]:
        raise click.ClickException(f"{path.name} needs STRATA_ALERT_EMAIL, a verified user email")
    left = re.findall(r"\{\{\w+\}\}", text)
    if left:
        raise click.ClickException(f"{path.name}: unrendered {sorted(set(left))}")
    return text


@click.command()
@click.argument("group", type=click.Choice(sorted(GROUPS)))
@click.option("--env", required=True, type=click.Choice(["dev", "test", "prod"]))
@click.option("--connection", default=None)
@click.option("--dry-run", is_flag=True)
def main(group: str, env: str, connection: str | None, dry_run: bool) -> None:
    out = ROOT / ".strata" / "sql" / env
    out.mkdir(parents=True, exist_ok=True)
    for pattern in GROUPS[group]:
        for path in sorted(ROOT.glob(pattern)):
            target = out / path.name
            target.write_text(render(path, env))
            click.echo(f"  {path.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
            if not dry_run:
                subprocess.run([os.environ.get("SNOW", "snow"), "sql", "-c", connection or f"scm_{env}", "-f", str(target)],
                               check=True)


if __name__ == "__main__":
    sys.exit(main())
