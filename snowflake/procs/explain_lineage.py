"""EXPLAIN_LINEAGE — trace the lineage of a metric from semantic view to source columns."""

from __future__ import annotations

from snowflake.snowpark import Session


def explain_lineage(session: Session, metric: str) -> dict:
    """Return the lineage path for a governed metric."""
    db = session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]

    try:
        lineage_df = session.sql(f"""
            SELECT *
            FROM TABLE(SNOWFLAKE.ACCOUNT_USAGE.GET_LINEAGE(
                '{db}.SEMANTIC.SCM_GOVERNED',
                'SEMANTIC_VIEW',
                'UPSTREAM',
                3
            ))
        """)
        rows = lineage_df.collect()

        path = []
        for row in rows:
            path.append({
                "source_object": str(row[0]) if row[0] else None,
                "source_column": str(row[1]) if row[1] else None,
                "target_object": str(row[2]) if row[2] else None,
                "target_column": str(row[3]) if row[3] else None,
            })

        return {
            "metric": metric,
            "view": f"{db}.SEMANTIC.SCM_GOVERNED",
            "lineage_depth": 3,
            "path": path,
        }
    except Exception as exc:
        return {"error": "lineage_failed", "message": str(exc), "metric": metric}
