"""Refuse a production release unless the commit passed every suite on SCM_TEST.

Reads EVAL.EVAL_RUNS for the commit: each of the seven suites must have a passing run, the
overall pass rate must meet the floor, and the latest AI Observability batch evaluation must too.
"""

from __future__ import annotations

import sys

import click

SUITES = ("metric_identity", "nl_accuracy", "persona_consistency", "governance", "resilience", "frontend", "supply_chain")


@click.command()
@click.option("--env", default="test")
@click.option("--sha", required=True)
@click.option("--floor", default=0.90, type=float)
def main(env: str, sha: str, floor: float) -> None:
    import snowflake.connector

    db = f"SCM_{env.upper()}"
    with snowflake.connector.connect(connection_name=f"scm_{env}", database=db) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT suite, MAX_BY(pass_rate, run_at), MAX_BY(passed = total, run_at) FROM {db}.EVAL.EVAL_RUNS "
                    "WHERE git_sha = %s GROUP BY suite", (sha,))
        runs = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
        cur.execute(f"SELECT MAX_BY(pass_rate, run_at) FROM {db}.EVAL.EVAL_RUNS WHERE suite = 'ai_observability_batch'")
        batch = cur.fetchone()[0]
    missing = [s for s in SUITES if s not in runs]
    failing = [s for s in SUITES if s in runs and not runs[s][1]]
    if missing or failing or batch is None or batch < floor:
        raise click.ClickException(f"release refused: missing {missing}, failing {failing}, "
                                   f"batch evaluation {batch} against a floor of {floor}")
    click.echo(f"release allowed for {sha}: seven suites green, batch evaluation {batch:.2%}")


if __name__ == "__main__":
    sys.exit(main())
