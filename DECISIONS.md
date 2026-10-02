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
