# Verification — 2026-10-03

What is new since docs/STATUS.md was last verified: the SPCS service, its endpoint, evaluator access,
the public mirror and the published repository. Everything else stands as STATUS.md reports it.

## Verdict: NO-GO, one P1, cleared by one command

| # | Severity | Finding | Clears when |
|---|---|---|---|
| 1 | P1 | HACK2SKILL_EVALUATOR_1 and _2 exist with the right role, warehouse and type, but have no password yet (`has_password = FALSE`), so evaluators cannot sign in. Setting it needs an admin sign-in that keeps the password out of the session transcript. | The admin runs `.venv/bin/python .strata/set_evaluator_passwords.py`; USERS then shows `has_password = TRUE`, `must_change_password = TRUE`. With that, GO. |
| 2 | P2 | Audit rows written through the service name STRATA_SERVICE as the user and the persona as the role; the signed-in user is only in the service logs. | The procedures take the caller from the request rather than CURRENT_USER(). |
| 3 | P2 | The service cannot suspend itself while it has a public endpoint (Snowflake docs), so it costs about 0.05 credits per hour until suspended by hand. | Suspend after the judging window; the first request resumes it. |

## Service

| Check | Result |
|---|---|
| SHOW SERVICES, SYSTEM$GET_SERVICE_STATUS | STRATA_SERVICE RUNNING, container READY on strata:4c3251f (the head of main), restart count 0 |
| Readiness probe | `/live`, 200 every 5 s in the container log |
| Logs | JSON request lines per call; `agent_no_governed_answer` lines name tools and statuses only |
| Rollback drill | acd23c5 → 21f4a17 → acd23c5, READY each time; endpoint checks green on 21f4a17 |
| Auto-resume | resumed on an endpoint request twice after ALTER SERVICE … SUSPEND; resume to READY 23 s on a warm pool |

## Endpoint persona and scope (`scripts/endpoint_check.py --ask`, key-pair token per the SPCS docs)

| Check | Result |
|---|---|
| Page routes (`/`, personas, meta, glossary, status, audit, governance, operations, lineage) | 9 of 9 return 200 with content |
| Persona follows the signed-in user | procurement, logistics and EMEA check users each pinned to their role |
| EMEA user | on-time by region returns EMEA only, as EMEA_PLANNING_ROLE |
| Logistics and supplier unit cost | refused (422); 0 values. Account side: through the same dimension procurement reads 8,001 of 8,001, logistics 0 |
| Ask | path `agent`, role LOGISTICS_ROLE, view LOGISTICS_SV_V1, hash c0e0370d… equal to the Builder's |

## Evaluator role, tested as JUDGE_ROLE from the admin session

| Check | Result |
|---|---|
| Reads | EVAL.EVAL_RUNS, AUDIT.ANSWERS, all five semantic views; SCM_AGENT listed |
| Column rule | supplier unit cost through LOGISTICS_SV_V1: 0 values |
| Denied | RAW, CONFORMED, SEMANTIC_BASE, STAGING; DELETE on EVAL and AUDIT; ALTER WAREHOUSE |
| Endpoint | JUDGE_ROLE holds STRATA_SERVICE!ALL_ENDPOINTS_USAGE |
| Users | TYPE PERSON, DEFAULT_ROLE JUDGE_ROLE, DEFAULT_WAREHOUSE SCM_WH_DEV, DEFAULT_SECONDARY_ROLES (), no network policy; no password yet (P1) |

## Mirror

| Check | Result |
|---|---|
| Without sign-in | https://strata-wine-one.vercel.app and its eight top-level pages plus a lineage page return 200 from a cookie-less client |
| Label | "Recorded demo data" and "Open the live app" in the shell on every page |
| Bundle scan | no key material; gitleaks clean; the only account identifier is the live-app link |

## Repository and CI

| Check | Result |
|---|---|
| History | filter-repo over all refs: workstation IP, example addresses and the admin username replaced; author and committer one no-reply identity |
| gitleaks | full history: no leaks |
| main | squashed to 70 commits in order, then 7 normal commits (77 with this one); only main is on GitHub |
| CI | build-and-test and supply-chain green on the head commit, no job skipped or disabled |
| README links | local links resolve; mirror 200; live app 302 to Snowflake endpoint sign-in |
