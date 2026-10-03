# How to evaluate STRATA

Three ways in, from least to most setup.

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
