# Status

Last updated 2026-10-03, after the closing run on account XZ02973 (Standard edition, GCP
me-central2). Standard edition: controls realised as compiled secure views; `docs/governance.md`
maps each control to what each edition provides.

## Evaluation on SCM_DEV (`make eval-account ENV=dev`)

| Suite | Passed | Notes |
|---|---|---|
| 1 · Metric identity against truth | 25 / 25 | includes the five canonical metrics, FY2026 and every month, through PROCUREMENT_SV_V1 |
| 2 · Words to governed query | 6 / 6 | agent:run over the 60-question set: 50 of 50 governed questions resolved to the right metric (floor 90%), 48 of 50 exact queries (floor 85%), 10 of 10 refusals; per-question outcomes in `eval/report/agent_floor.json`. The two inexact answers chose the wrong window: q13 (DIO by month) read September 2026 alone instead of FY2026, q15 (landed cost by month across the tariff step) read April to June 2026 instead of FY2026 |
| 3 · One question, three roles, one hash | 24 / 24 | 20 cases × 3 roles identical with hashes equal to the local engine's (`eval/report/persona_account.md`); the 20 hashes are unchanged after supplier_unit_cost was exposed |
| 4 · Governance rules | 36 / 36 | adds the masking demonstration: through the same dimension PROCUREMENT_ROLE reads 8,001 of 8,001 supplier unit costs and LOGISTICS_ROLE 0 of 8,001; deployed views round-trip with the 19 governed expressions; the agent spec names every default and every governed metric and dimension |
| 5 · Resilience and operations | 9 / 9 | Time Travel restore drill failed in the full run (the test named SCM_TEST and cloned a transient table as permanent); fixed and passed on re-run |
| 6 · Front end | 7 / 7 | |
| 7 · Software supply chain | 5 / 5 | |

The full run reported 102 of 104 before this run; the restore drill was fixed then, and the
agent floor, the persona hashes and the governance suite were re-run on their own here, all green; suites 1, 5, 6 and 7 hold from the earlier run and nothing they cover changed. On the current
commit the full `make eval-account` was not repeated.

## Deployed on SCM_DEV

| Area | State |
|---|---|
| Roles, monitor (40 credits), XS warehouse, schemas, stages, network policy on the two service users | green |
| RAW load: 22 files, row counts equal to the files | green |
| dbt in Snowflake: 72 of 72; delivery-event dynamic table incremental | green |
| Entitlement registry, 10 secure views in SEMANTIC_BASE, tags on 7 columns | green |
| Five semantic views over SEMANTIC_BASE: round-trip, 19 identical metric expressions; supplier_unit_cost in PROCUREMENT_SV_V1 and LOGISTICS_SV_V1 only | green |
| Cortex Search over 5,039 documents; AI_CLASSIFY agreement 96.6% | green |
| GOVERNED_QUERY, DESCRIBE_METRIC, EXPLAIN_LINEAGE; audit row per answer and refusal | green |
| SCM_AGENT (three procedures and Search), SCM_EXPLORE_AGENT (Analyst, SCM_DEPLOY), SCM_STEWARD | green |
| Operational loop and weekly cost task | green, resumed |
| Alerts: dbt test failure, evaluation regression, SLO breach | green, resumed |
| Stale-source alert | suspended on DEV, which loads once (`stale_source_alert` in dev.yaml) |
| Nightly-eval Cortex Code routine | suspended; the task loop runs dbt and evaluation at warehouse cost (DECISIONS.md) |
| SPCS service | blocked: Docker |
| Public mirror on Vercel | blocked: token |

## Needs Enterprise edition, or a blocked step

- Row access and masking policies on CONFORMED (compiled in `snowflake/policies/enterprise/`).
- GET_LINEAGE parity for EXPLAIN_LINEAGE.
- A per-database event table; Time Travel beyond one day.
- The service, its rollback drill and the Sf-Context-Current-User check: blocked: Docker.
- The public mirror and `/query` through the service user from it: blocked: token.
- The account-level network policy: applied only to the service users; the account policy needs
  the team's origins and a COMPUTE_POOL rule for the service.
- `tasks/verify.md`: absent from the repository.

## Local checks on this commit

| Check | Result |
|---|---|
| `scripts/reproducible.sh` | 188 files byte-identical across two runs |
| `pytest ontology/tests eval` | 106 passed, 19 skipped (account checks) |
| `pytest api/tests` | 23 passed |
| `ruff check .` | clean |
| `npm run build`, `npm run lint`, Playwright | not re-run; no front-end change since 78 of 78 |

## Preview findings (2026-10-03, `make preview` against SCM_DEV)

All ten pages render against live data with no page errors and no failed /api calls. The three
findings from the first preview are fixed in the repository:

| Page | Finding | Now |
|---|---|---|
| Governance | Evaluation read the last local report; the agent card named SCM_PROD and claude-4-sonnet from a committed snapshot | Latest batch in EVAL.EVAL_RUNS (113 of 113, 2 need the account); agent card from DESCRIBE AGENT: SCM_DEV.AGENT.SCM_AGENT, claude-sonnet-4-6, four tools |
| Operations | Every alert NOT_RUN; credits 0; p95 1590 ms against 1500 ms | OPS.ALERT_STATUS() as the alerts' owner: three started, STALE_SOURCE_ALERT suspended, last outcomes and SLO_BREACH_ALERT's firing at 09:36; credits this week 5.38 (warehouse); target 2500 ms, measured 1414 ms, met |
| Ask, Compare | The Next dev proxy cut agent answers off at 30 s | preview config raises it to 240 s |

The cost row counts warehouse, compute-pool and Cortex function credits; Cortex Agents and Cortex
Code credits are not in it, so it reads well below the account's spend.
