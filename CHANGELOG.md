# Changelog

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
