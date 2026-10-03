# Status

Last updated 2026-10-03, after the DEV deployment on account XZ02973 (Standard edition, GCP
me-central2). Standard edition: controls realised as compiled secure views; `docs/governance.md`
maps each control to what each edition provides.

## Evaluation on SCM_DEV (`make eval-account ENV=dev`)

| Suite | Passed | Notes |
|---|---|---|
| 1 · Metric identity against truth | 25 / 25 | includes the five canonical metrics, FY2026 and every month, through PROCUREMENT_SV_V1 |
| 2 · Words to governed query | 5 / 6 | agent floor failed: 44 of 50 governed questions resolved to the right metric through agent:run (88% against a 90% floor); the exact-match and refusal counts were not reported, because the assertion stopped at the first floor. Unqualified "fill rate" went to a variant in at least three questions |
| 3 · One question, three roles, one hash | 24 / 24 | 20 cases × 3 roles identical with hashes equal to the local engine's (`eval/report/persona_account.md`); every numeric agent answer reconciled to an AUDIT.ANSWERS row |
| 4 · Governance rules | 28 / 28 | each role's scope through its semantic view, EMEA_PLANNING_ROLE limited to EMEA; CONFORMED, RAW, SEMANTIC_BASE denied; 42 column rules evaluated per role; all SEMANTIC_BASE views secure |
| 5 · Resilience and operations | 9 / 9 | Time Travel restore drill failed in the full run (the test named SCM_TEST and cloned a transient table as permanent); fixed and passed on re-run |
| 6 · Front end | 7 / 7 | |
| 7 · Software supply chain | 5 / 5 | |

The full run reported 102 of 104; the restore drill was fixed and re-run green, so 103 of 104 hold
on the current commit. The agent floor is the one failing check.

## Deployed on SCM_DEV

| Area | State |
|---|---|
| Roles, monitor (40 credits), XS warehouse, schemas, stages, network policy on the two service users | green |
| RAW load: 22 files, row counts equal to the files | green |
| dbt in Snowflake: 72 of 72; delivery-event dynamic table incremental | green |
| Entitlement registry, 10 secure views in SEMANTIC_BASE, tags on 7 columns | green |
| Five semantic views over SEMANTIC_BASE: round-trip, 19 identical metric expressions | green |
| Cortex Search over 5,039 documents; AI_CLASSIFY agreement 96.6% | green |
| GOVERNED_QUERY, DESCRIBE_METRIC, EXPLAIN_LINEAGE; audit row per answer and refusal | green |
| SCM_AGENT (three procedures and Search), SCM_EXPLORE_AGENT (Analyst, SCM_DEPLOY), SCM_STEWARD | green |
| Operational loop, weekly cost task, four alerts, nightly-eval automation (03:30 UTC) | green, resumed |
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
| `pytest ontology/tests api/tests eval` | 125 passed, 15 skipped (account checks) |
| `ruff check .`, authorship lint | clean |
| `npm run build`, `npm run lint` | pass |
| Playwright at 390, 1024, 1440 with axe and CSP | 78 of 78 |
