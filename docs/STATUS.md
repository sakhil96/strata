# Status

Last updated 2026-10-03, after the finishing run on account XZ02973 (Standard edition, GCP
me-central2). Standard edition: controls realised as compiled secure views; `docs/governance.md`
maps each control to what each edition provides.

## Evaluation on SCM_DEV

The latest batch in EVAL.EVAL_RUNS, which the governance page reads, ran every suite against SCM_DEV
with the agent off: 113 of 113 checks passed, and 2 need the account (the agent floor and the
held-out pass), which ran on their own in this and the previous run. The governance suite was
re-run after the service-identity change: 39 of 39.

| Suite | Passed | Notes |
|---|---|---|
| 1 · Metric identity against truth | 25 / 25 | includes the five canonical metrics, FY2026 and every month, through PROCUREMENT_SV_V1 |
| 2 · Words to governed query | 7 / 7, and the agent floor on its own | agent:run over the 60-question set: 50 of 50 governed questions resolved to the right metric (floor 90%), 48 of 50 exact queries (floor 85%), 10 of 10 refusals; per-question outcomes in `eval/report/agent_floor.json`. The two inexact answers chose the wrong window: q13 (DIO by month) read September 2026 alone instead of FY2026, q15 (landed cost by month across the tariff step) read April to June 2026 instead of FY2026 |
| 2b · Held-out questions | 10 / 10 | `eval/questions_heldout.yaml`, one agent:run pass: 10 of 10 resolved, 10 of 10 exact, against 50 / 50 and 48 / 50 on the tuned set; ten questions, so read it as at least about 72% (95% Wilson), and the spec lists the filter values the held-out questions use |
| 3 · One question, three roles, one hash | 24 / 24 | 20 cases × 3 roles identical with hashes equal to the local engine's (`eval/report/persona_account.md`); the 20 hashes are unchanged after supplier_unit_cost was exposed |
| 4 · Governance rules | 39 / 39 | the service assumes exactly the four personas through SCM_SERVICE_PERSONAS, none in its default session; nothing committed names an environment or an undeployed model; the masking demonstration: through the same dimension PROCUREMENT_ROLE reads 8,001 of 8,001 supplier unit costs and LOGISTICS_ROLE 0 of 8,001; deployed views round-trip with the 19 governed expressions; the agent spec names every default and every governed metric and dimension |
| 5 · Resilience and operations | 9 / 9 | includes the Time Travel restore drill |
| 6 · Front end | 7 / 7 | |
| 7 · Software supply chain | 4 / 4 | one check skipped locally |

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
| Operational loop; cost task daily with a week-to-date row (5.38 credits this week) | green, resumed |
| Alert status for readers: OPS.ALERT_STATUS(), owner's rights | green |
| Service identity: SCM_SERVICE_PERSONAS (four personas) on SCM_SERVICE_USER, no default secondary roles | green |
| Team-origin network rule | re-pointed to the deploying workstation's current /32 |
| Alerts: dbt test failure, evaluation regression, SLO breach | green, resumed |
| Stale-source alert | suspended on DEV, which loads once (`stale_source_alert` in dev.yaml) |
| Nightly-eval Cortex Code routine | suspended; the task loop runs dbt and evaluation at warehouse cost (DECISIONS.md) |
| SPCS service | green: STRATA_SERVICE on SCM_POOL_DEV (CPU_X64_XS), READY; endpoint checks as three check users, rollback drill; see the 2026-10-03 service section below |
| Public mirror on Vercel | green: https://strata-wine-one.vercel.app, recorded demo data, no sign-in |
| History rewrite and push | green: scrubbed with filter-repo, gitleaks clean, 70 commits on main, github.com/sakhil96/strata; CI green |

## Needs Enterprise edition, or a blocked step

- Row access and masking policies on CONFORMED (compiled in `snowflake/policies/enterprise/`).
- GET_LINEAGE parity for EXPLAIN_LINEAGE.
- A per-database event table; Time Travel beyond one day.
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

## Ask governance fixes (2026-10-03)

- A: Ask runs each canonical query the agent settles on through GOVERNED_QUERY as the caller's persona.
  EMEA_PLANNING_ROLE answers on PLANNING_SV_V1 with EMEA plants only; DEV governance and persona
  suites: 64 passed (includes the EMEA Ask-equals-Builder test), 20 persona hashes identical to before.
- B: the lead sentence comes from the persona's own result (api/narrate.py); the agent's reading is at
  most two sentences and is dropped if it holds an amount, a hash or talk of its instructions.
- C: `across_tariff_step` (Apr to Sep 2026) returns one series, hash 12b54789, July low $148.46. The 19
  metric expressions are unchanged in all five views; only q15's verified query window moved.
- D: linear chart with a dot per month, marker only inside the domain, "Apr 2026" dates, registry
  titles with units in table headers, ledger role/view and both latencies. Four Try questions as
  planning, procurement, logistics and EMEA at 1440 and 390 looked at. Playwright with axe: 78 passed
  at 390, 1024 and 1440. Web build and lint pass. Ten of the fifty questions (the misses q09 q24 q29
  q39 q40 q41 q42 q43, plus q13 and q15) through agent:run: all ten resolve, 10/10 exact after one fix
  to the tariff wording (q43 had taken the across window).
- E: stopped at step 15; see docs/DECISIONS.md. Docker Desktop's server runs, but calling agent:run
  from inside SPCS probably needs a key or PAT in the container.
- Known: status line reads "DATA AS OF UNKNOWN" (freshness source not wired); a 40-bar chart is
  replaced by the table alone.

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

## Service, evaluator access and publication (2026-10-03)

- Live app: https://mbloac-dzvlnoz-zv32033.snowflakecomputing.app, STRATA_SERVICE on image 4c3251f.
  `scripts/endpoint_check.py` as the three check users: 9 page routes 200, each user pinned to its
  persona, the EMEA user sees EMEA only, logistics reads no supplier unit cost, Ask resolves through
  the agent (path `agent`) as LOGISTICS_ROLE on LOGISTICS_SV_V1 in about 27 s.
- Fixed on the way: the governed procedures failed inside agent:run from SPCS (no current database);
  persona roles lacked the endpoint service role. Both recorded in DECISIONS.md.
- Rollback drill: acd23c5 → 21f4a17 → acd23c5, READY each time, checks green on the older image.
- Cost: SCM_POOL_DEV meters about 0.05 credits per running hour. The service resumes on an endpoint
  request; it cannot suspend itself (AUTO_SUSPEND_SECS is not supported with a public endpoint), so it
  is suspended by hand after an evaluation. Resume to READY on a warm pool: 23 s.
- Evaluators: HACK2SKILL_EVALUATOR_1 and _2, default role JUDGE_ROLE; JUDGE_ROLE reads the five views,
  EVAL and AUDIT, uses the agent and the endpoint, and is denied RAW, STAGING, CONFORMED and
  SEMANTIC_BASE. SCM_READER no longer holds USAGE on those schemas.
- CI: green after four fixes (tests for the procedures and the agent parser, the browser checks'
  Python, a stale date assertion, the image's unused wheel and setuptools).
- Known: audit rows from the service record the service as the user (STRATA_SERVICE) and the persona
  as the role; the signed-in user is in the service logs, not in AUDIT.ANSWERS.
