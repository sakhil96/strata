"""Governance tests: agent tools, policies, lineage, round-trip, grants."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

AGENT_SQL_PATH = Path(__file__).resolve().parent.parent / "snowflake" / "agent" / "create_agent.sql"
INSTRUCTIONS_PATH = Path(__file__).resolve().parent.parent / "snowflake" / "agent" / "instructions.md"


class TestGovernanceConstraints:
    def test_agent_has_only_three_tools(self):
        sql = AGENT_SQL_PATH.read_text()
        assert "GOVERNED_QUERY" in sql
        assert "DESCRIBE_METRIC" in sql
        assert "EXPLAIN_LINEAGE" in sql
        # No SQL tool
        assert "SQL_TOOL" not in sql
        assert "sql_tool" not in sql

    def test_instructions_forbid_raw_sql(self):
        instructions = INSTRUCTIONS_PATH.read_text()
        lower = instructions.lower()
        assert "no sql tool" in lower
        assert "never write or execute sql directly" in lower

    def test_instructions_have_refusal_policy(self):
        instructions = INSTRUCTIONS_PATH.read_text()
        assert "refusal" in instructions.lower() or "Refuse" in instructions

    def test_instructions_have_resolution_policy(self):
        instructions = INSTRUCTIONS_PATH.read_text()
        assert "resolution" in instructions.lower() or "Resolution" in instructions

    def test_instructions_require_answer_contract(self):
        instructions = INSTRUCTIONS_PATH.read_text()
        assert "semantic_query_hash" in instructions
        assert "lineage" in instructions
        assert "role" in instructions

    def test_no_table_names_in_instructions(self):
        instructions = INSTRUCTIONS_PATH.read_text()
        # The instructions should not contain raw table names
        assert "RAW.SUPPLIERS" not in instructions
        assert "CONFORMED.FCT_" not in instructions
        assert "STAGING.STG_" not in instructions
