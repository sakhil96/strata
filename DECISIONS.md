# DECISIONS.md — Architecture and design decisions

## 2026-10-02: Repository initialised from scratch

We start from an empty directory. No template, no scaffold. Every file is hand-written
or compiler-generated from the ontology.

## 2026-10-02: LinkML for the ontology

LinkML gives us typed YAML with inheritance, generates Pydantic models, JSON Schema,
OWL and ER diagrams from one source. The supply chain domain fits its class/slot model
naturally. We vendor no LinkML runtime into the application; it is a build-time dependency.

## 2026-10-02: Fiscal year starts 1 October

Aligns with the US federal fiscal year and a common multinational calendar. The data
generator creates exactly one fiscal year: FY2026 (1 Oct 2025 to 30 Sep 2026).

## 2026-10-02: Single accent colour (--ore #E36F2E)

One accent reduces decision fatigue and makes the active element unambiguous. Every other
colour in the palette is neutral. We reserve green, yellow and red for status only.

## 2026-10-02: Three environments as separate databases

SCM_DEV, SCM_TEST, SCM_PROD. Separate databases rather than schemas because Snowflake
network policies, resource monitors and grants are easier to reason about at the database
level, and it mirrors how enterprises actually operate.

## 2026-10-02: No SQL tool on the agent

The agent has only GOVERNED_QUERY, DESCRIBE_METRIC and EXPLAIN_LINEAGE. This makes every
answer auditable and every metric traceable. The cost is that ad-hoc exploration must
go through the Builder or Cortex Analyst with instructions that route metric questions
back to GOVERNED_QUERY.

## 2026-10-02: Ratios are ratios of sums

We never average pre-computed ratios. on_time_delivery at the region level is
count(on_time lines in region) / count(all lines in region), not avg(plant-level OTD).
This is mathematically correct and avoids Simpson's paradox.

## 2026-10-02: DuckDB + dbt-core + Cube for local fallback

Developers and CI run the full pipeline without Snowflake credentials. The same ontology
and registry produce dbt models targeting DuckDB and Cube views. `make local-demo`
stands up the entire stack on a laptop.

## 2026-10-02: Rebuild history before publishing

The first two commits bundled 164 files, which hid the order we built things in and broke our
own one-change-per-commit rule. Before the repository goes public we replayed the same tree as
61 commits by area in build order. The tree at the new head is byte-identical to the old one
(`git diff pre-rebuild` is empty). The old history stays on the local `pre-rebuild` branch until
the first public push, then we delete it. No team author identity is configured on this machine,
so commits carry the local default; we re-author before pushing.

## 2026-10-02: Audit before closing gaps

docs/GAPS.md records each specification item as present, partial or absent with the command that
proved it. We close gaps in priority order, one commit per gap.

## Lock the image for Linux, not for the laptop

The runtime and dev locks are resolved for `x86_64-manylinux_2_28`, the image platform. An earlier
`cryptography<46` pin existed only because cryptography 50 has no Intel macOS wheel; it shipped
eight advisories (fixed in 46.0.5 to 50.0.0) and pyOpenSSL 25 two more. Lifting it required
snowflake-connector-python 4.x, which in turn required dbt-snowflake 1.10+, so the build extra moved
to dbt-core 1.11 and dbt-duckdb 1.10. The local DuckDB build passes 78 of 78 on the new dbt. The
Snowflake paths on connector 4 have not been run against an account yet.

## The service holds no secret

The SPCS container authenticates with the session token Snowflake mounts at
`/snowflake/session/token`. A `secrets:` block would add a credential to rotate and nothing else, so
the service spec has none. Key-pair JWT is used only by CI and by laptops.

## Cortex Analyst is an exploration tool, not an answering tool

The spec lists Cortex Analyst among the agent's tools and also says numbers come only from
GOVERNED_QUERY. Both hold: the agent may call Analyst to explore phrasing, but `api/agent.py` parses
numbers only from GOVERNED_QUERY results, and the governance suite fails if any other tool's output
reaches an answer.
