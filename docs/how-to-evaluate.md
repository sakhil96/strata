# How to evaluate STRATA

## Evaluator access

The live app runs in Snowpark Container Services on the SCM_DEV environment.

| | |
|---|---|
| Account URL | https://dzvlnoz-zv32033.snowflakecomputing.com |
| App (service endpoint) | https://mbloac-dzvlnoz-zv32033.snowflakecomputing.app |
| Users | `HACK2SKILL_EVALUATOR_1`, `HACK2SKILL_EVALUATOR_2`; login names and temporary passwords are sent to the organisers separately |
| Role | `JUDGE_ROLE`, the default; no secondary roles |

First sign-in, as the Snowflake docs describe it:

1. Open the account URL and sign in with the login name and temporary password. The password is set to
   expire on first use, so Snowsight asks for a new one straight away.
2. Snowsight then asks you to enrol in multi-factor authentication: a passkey (recommended), an
   authenticator app with one-time codes, or Duo. Password sign-in to Snowsight needs a second factor
   for every human user, so this step cannot be skipped.
3. Open the app URL and sign in through the same account, with the new password and second factor.

In the app you may switch among all personas on the dial, EMEA planning included; every answer shows
the role and the semantic view it ran on. JUDGE_ROLE is read-only: SELECT on the five semantic views,
read access to EVAL and AUDIT, USAGE on SCM_AGENT and the XSMALL warehouse SCM_WH_DEV, and nothing in
RAW, STAGING, CONFORMED or SEMANTIC_BASE. Its one write is the audit row GOVERNED_QUERY appends
for each answer it gives you, which is what makes your questions show on the Governance page.

The app can take about half a minute to answer the first request after a quiet spell while the
service resumes.

Three other ways in, from least to most setup.

## 1. The public mirror (no install)

A static build of the front end with answers recorded from the local build (`make demo-mirror`).
Every page works; Ask and Compare replay the questions offered on screen. Typed questions that were
not recorded say so instead of guessing. The Builder answers live only when the mirror is built with
`STRATA_API` pointing at a service-user API.

## 2. A laptop, no Snowflake (about five minutes)

Python 3.11 and Node 22.

```
uv venv .venv --python 3.11 && uv pip install -r requirements-dev.lock
cd web && npm ci && cd ..
make local-demo          # data, dbt on DuckDB, compile, web build, API on :8000
make eval                # seven suites; account-only checks report needs_account
```

Open http://127.0.0.1:8000. The same canonicaliser, query hash and SQL renderer run here as in
the procedures, so hashes match what Snowflake returns for the same question.

## 3. Your Snowflake account (Enterprise edition, for GET_LINEAGE)

```
make setup ENV=dev CONN=scm_dev      # roles incl. JUDGE_ROLE, schemas, policies, monitors, ops
make load ENV=dev CONN=scm_dev
make release ENV=dev CONN=scm_dev        # objects, views, procedures, agent; then grants
make loop ENV=dev CONN=scm_dev           # freshness, dbt and eval tasks
make smoke ENV=dev CONN=scm_dev
make eval-account ENV=dev CONN=scm_dev
```

Grant `JUDGE_ROLE` to your user. It reads the persona views, the glossary and the audit trail and
cannot see RAW or CONFORMED.

## What to check

| Claim | Where to look |
|---|---|
| One definition, three vocabularies, one number | Compare page; `eval/test_persona_consistency.py`; on SCM_DEV, `eval/report/persona_account.md`: 20 cases × 3 roles through GOVERNED_QUERY, identical rows and hashes, hashes equal to the local engine's |
| Numbers match an independent truth | `eval/test_metric_identity.py`, every metric × month × plant × region × segment × family |
| Legacy numbers disagree for stated reasons | Before/after page; `api/legacy.py` |
| The agent cannot answer outside the procedures | Governance page; `eval/test_governance.py` |
| A governed column is masked by role (the masking demonstration) | See below |
| Refusals for raw SQL, table access, injection | Ask page; `eval/questions.yaml` refusals |
| Builds are reproducible | `make reproducible` |

## Words to governed query: tuned set and held-out set

| Set | Questions | Metric resolved | Exact query | Refusals |
|---|---|---|---|---|
| `eval/questions.yaml`, tuned against | 50 + 10 refusals | 50 / 50 (100%) | 48 / 50 (96%) | 10 / 10 |
| `eval/questions_heldout.yaml`, never tuned against | 10 | 10 / 10 (100%) | 10 / 10 (100%) | — |

Both through agent:run as EXECUTIVE_ROLE on SCM_DEV, 2026-10-03; per-question outcomes in
`eval/report/agent_floor.json` and `eval/report/heldout.json`. The held-out questions reuse no
phrasing and no filter value from the tuned set. Read the 10 / 10 with two caveats: ten questions
bound the true rate only from about 72% upward (95% Wilson), and the agent's tool description lists
every filter value and plant name, so the held-out set avoids the tuned questions' values but not
the spec's. A judge's own wording is the real held-out test: `SCM_HELDOUT=on pytest eval/test_nl_accuracy.py`
after adding questions to the file.

## The masking demonstration

`ontology/entitlements.yaml` shows FCT_PO_LINE.UNIT_COST to SCM_ADMIN and PROCUREMENT_ROLE and
returns null to everyone else. The column is exposed as `po_lines.supplier_unit_cost` in exactly two
semantic views, PROCUREMENT_SV_V1 and LOGISTICS_SV_V1, so the rule can be seen from both sides of
the same dimension:

```sql
USE ROLE PROCUREMENT_ROLE;   -- every line carries a cost
SELECT COUNT(*), COUNT(supplier_unit_cost) FROM SEMANTIC_VIEW(SCM_DEV.SEMANTIC.PROCUREMENT_SV_V1
  DIMENSIONS po_lines.po_line_id, po_lines.supplier_unit_cost);
USE ROLE LOGISTICS_ROLE;     -- the same lines, every cost null
SELECT COUNT(*), COUNT(supplier_unit_cost) FROM SEMANTIC_VIEW(SCM_DEV.SEMANTIC.LOGISTICS_SV_V1
  DIMENSIONS po_lines.po_line_id, po_lines.supplier_unit_cost);
```

Standard edition: controls realised as compiled secure views, so the rule is the CASE in
SEMANTIC_BASE.FCT_PO_LINE; on Enterprise it is the tag-based masking policy MASK_FCT_PO_LINE_UNIT_COST.
No metric reads the column, so the 19 metric expressions and every persona hash are unchanged.
The governance suite (suite 4) checks it: `test_only_the_procurement_and_logistics_views_expose_supplier_unit_cost`,
`test_exposing_a_governed_column_leaves_every_metric_expression_as_the_governed_view_has_it`, and on
the account `test_on_the_account_supplier_unit_cost_shows_or_nulls_as_the_registry_says` and
`test_on_the_account_the_deployed_views_round_trip_with_the_governed_expressions`.
