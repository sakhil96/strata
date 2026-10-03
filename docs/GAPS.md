# Gap audit against the build specification

Audited 2026-10-02 at commit e9a97f5. Evidence is the command output we ran; "needs account"
means the artefact can be written and validated locally but only proven on Snowflake.

| # | Item | State at audit | Evidence |
|---|------|----------------|----------|
| 1 | VQR target | absent | `grep -c verified_queries` = 0 in compile.py and all five YAMLs. The YAML itself had no `tables`, `dimensions`, `facts` or metric `expr`, so it was not a valid semantic view either. |
| 2 | Ground truth by month x plant x region x segment x family | partial | truth rows keyed by month only; 4 of 11 metrics; no variants |
| 3 | /compare, /before-after | absent | `api/routes/` has no compare or before_after module; /meta present |
| 4 | Ten pages, Index, Lineage, Chart, contour canvas | partial | 8 of 10 pages (no /lineage/[metric], /styleguide); no index, lineage or chart component; no canvas |
| 5 | Cortex Code context | partial | AGENTS.md and 8 skills present but as flat files, not `skills/<name>/SKILL.md`; no commands, no subagents, hooks.json empty, .mcp.json empty, `tasks/` empty, no docs/built-with-coco.md |
| 6 | Analyst + Search tools, Steward agent, tasks, MCP server | absent | create_agent.sql lists only the three procedures; no `snowflake/tasks/`; no `agent/mcp_server.py` |
| 7 | Unstructured layer | absent | no notes, contract excerpts or SOP pages in generate.py; no Cortex Search script |
| 8 | 40 to 80 commits | absent | `git log --oneline | wc -l` = 2 |
| 9 | load log, freshness, hts_2026.csv, gscpi.csv | partial | load.py has the log and freshness; both CSVs missing |
| 10 | dynamic table, fct_fx_rate, lead_time_variability, registry fields | partial | fct_fx_rate present; registry fields present; lead_time_variability only as a variant; no dynamic table |
| 11 | JUDGE_ROLE, demo mode, how-to-evaluate | absent | no JUDGE in 01_roles.sql; no demo build; no doc |
| 12 | Documents | partial | demo_script.md and judging_checklist.md missing; design.md has no QA checklist |
| 13 | Front-end QA | absent | `web/tests/e2e/` empty; no screenshots, lint rules or Lighthouse script |
| 14 | Supply chain in CI | partial | pip-audit and pnpm audit run with `|| true` (never block); no SBOM, no image scan |
| 15 | Databricks target | absent | listed in `--target` choices but no generator; selecting it emitted nothing |

## Defects found during the audit

- `ontology/ontology.yaml` began with the compiler's generated-file header although it is the source.
- `GOVERNED_QUERY._build_where` interpolated filter values into SQL without validation.
- docs/STATUS.md and the previous turn's summary marked Days 10 to 14 complete; they were not.
- No Node toolchain on this machine; we used a portable Node 22 in /tmp for builds.

## Closure

| # | Closed | Notes |
|---|---|---|
| 1 | yes | verified queries compiled from eval/questions.yaml into every view |
| 2 | yes | truth for every metric and variant at every grouping, compared in suite 1 |
| 3 | yes | routes and pages wired; recorded for the mirror |
| 4 | yes | ten pages, components, contour field, states, footer status line |
| 5 | yes | plugin validated; 8 skills, 7 commands, 4 subagents, guard hooks, .mcp.json, tasks/day01-14 |
| 6 | written, needs account | agent, steward agent, task loop, MCP server |
| 7 | written, needs account for AI functions and search | documents generated and modelled |
| 8 | yes | 80 commits; pre-rebuild and pre-squash branches kept locally |
| 9 | yes, except gscpi.csv | fetched, not committed (terms unconfirmed) |
| 10 | yes; dynamic table needs account | |
| 11 | yes; service user and JUDGE_ROLE need account | demo build verified |
| 12 | yes | |
| 13 | yes; Lighthouse script written, not run (no Chrome for Lighthouse here) | |
| 14 | yes; runs on first push | the audit also found and fixed cryptography, pyOpenSSL and PostCSS advisories |
| 15 | Databricks compiled; Marketplace and CoWork as notes | |
