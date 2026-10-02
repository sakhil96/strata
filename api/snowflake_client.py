"""Snowflake connection client using the signed-in user's context."""

from __future__ import annotations

import os

import snowflake.connector


def get_connection(persona: str | None = None):
    """Return a Snowflake connection using the current user context.

    In SPCS, reads Sf-Context-Current-User from the request headers.
    Locally, uses the connection profile from ~/.snowflake/connections.toml.
    """
    env = os.getenv("SCM_ENV", "dev").upper()
    db = f"SCM_{env}"
    wh = f"SCM_WH_{env}"

    conn = snowflake.connector.connect(
        connection_name=os.getenv("SNOWFLAKE_CONNECTION_NAME", "default"),
        database=db,
        warehouse=wh,
        schema="AGENT",
    )

    if persona:
        conn.cursor().execute(f"USE ROLE {persona}")

    return conn


def execute_procedure(conn, proc_name: str, *args) -> dict:
    """Call a stored procedure and return the result as a dict."""
    cursor = conn.cursor()
    placeholders = ", ".join(["%s"] * len(args))
    cursor.execute(f"CALL {proc_name}({placeholders})", args)
    result = cursor.fetchone()
    if result and result[0]:
        import json
        return json.loads(result[0])
    return {}
