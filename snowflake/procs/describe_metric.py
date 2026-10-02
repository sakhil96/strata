"""DESCRIBE_METRIC — return the governed definition, lineage and metadata for a metric."""

from __future__ import annotations

from snowflake.snowpark import Session


def describe_metric(session: Session, name: str) -> dict:
    """Look up a metric in the glossary and return its full definition."""
    db = session.sql("SELECT CURRENT_DATABASE()").collect()[0][0]

    try:
        df = session.sql(f"""
            SELECT metric_name, title, definition, formula_text,
                   owner, steward, version, status, scor_attribute,
                   unit, grain, date_basis, synonyms, variants
            FROM {db}.SEMANTIC.GLOSSARY
            WHERE metric_name = '{name.lower()}'
        """)
        rows = df.collect()
        if not rows:
            # Try fuzzy match
            all_df = session.sql(f"SELECT metric_name FROM {db}.SEMANTIC.GLOSSARY")
            all_names = [r[0] for r in all_df.collect()]
            return {
                "error": "metric_not_found",
                "name": name,
                "available_metrics": all_names,
            }

        row = rows[0]
        return {
            "metric_name": row[0],
            "title": row[1],
            "definition": row[2],
            "formula_text": row[3],
            "owner": row[4],
            "steward": row[5],
            "version": row[6],
            "status": row[7],
            "scor_attribute": row[8],
            "unit": row[9],
            "grain": row[10],
            "date_basis": row[11],
            "synonyms": row[12],
            "variants": row[13],
        }
    except Exception as exc:
        return {"error": "lookup_failed", "message": str(exc)}
