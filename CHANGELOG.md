# Changelog

## [1.1.0] - 2026-10-03

### Added
- The application in Snowpark Container Services with a public endpoint; `scripts/endpoint_check.py`
  checks persona pinning, EMEA scope, column rules and the agent path as the endpoint-check users.
- Evaluator access through JUDGE_ROLE: every persona view, EVAL, AUDIT, the agent and the endpoint.
- The public mirror on Vercel, labelled as recorded demo data on every page with a link to the live app.
- `docs/overview.md`; tests for the governed procedures and the agent reply parser.

### Fixed
- The governed procedures take their database from their DDL, so they answer inside agent:run from SPCS.
- Persona roles and JUDGE_ROLE hold the endpoint service role on every service apply.
- SCM_READER no longer holds USAGE on RAW, STAGING, CONFORMED or SEMANTIC_BASE.
- The image drops the base image's wheel and setuptools; the browser checks start with any Python.

## [1.0.0] - 2026-10-02

### Added
- LinkML ontology and a metric registry of 11 metrics and 8 variants, compiled to Snowflake semantic
  views (governed plus four personas) with verified queries, dbt schema, glossary, Ossie, Cube,
  Databricks metric views, LinkML artefacts and an ER diagram.
- Deterministic synthetic world with independent truth, four messy sources and content documents.
- dbt project portable between DuckDB and Snowflake, including AI_CLASSIFY and AI_FILTER note models.
- GOVERNED_QUERY, DESCRIBE_METRIC and EXPLAIN_LINEAGE procedures; SCM_AGENT and a Steward agent;
  Cortex Search over notes; MCP server; operational task loop; dynamic table for delivery events.
- FastAPI service with query, ask, compare, before-after, meta, glossary, lineage, audit, status and
  operations; strict CSP with per-page hashes.
- STRATA front end: ten pages, design tokens, fallback and empty states, public mirror build.
- Seven evaluation suites with a report; Playwright and axe at three widths.
- Hash-locked dependencies, SBOMs, image scan, release gate, SPCS deploy and rollback.
- Cortex Code plugin: skills, commands, subagents, guard hooks, MCP config.

### Security
- Lifted the cryptography pin; locks resolved for the image platform (see docs/DECISIONS.md).
