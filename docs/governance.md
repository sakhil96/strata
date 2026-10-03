# Governance

Who may see which rows and columns is declared once, in `ontology/entitlements.yaml`, and compiled
with the rest of the ontology. Numbers reach people only through `GOVERNED_QUERY`, which runs with
the caller's rights against that caller's semantic view and writes one `AUDIT.ANSWERS` row per
answer or refusal, keyed by the `semantic_query_hash` it returns.

## The paths to a number

| Path | Who | What it can return |
|---|---|---|
| `SCM_AGENT` (agent:run, the Ask page) | persona roles, JUDGE_ROLE, the service role | Numbers from `GOVERNED_QUERY` only; definitions, lineage, and note citations from Cortex Search |
| `GOVERNED_QUERY` directly (the Builder, the API) | the same roles | The answer contract: rows, hash, SQL, lineage, role |
| `SCM_EXPLORE_AGENT` | SCM_DEPLOY only | Cortex Analyst over `SCM_GOVERNED`; exploration for engineers, never a governed answer |

The answer agent's tool set is the enforcement: it has no tool that returns a number except
`GOVERNED_QUERY`. On the DEV account, before Cortex Analyst was removed from it, the model answered
from the SQL Analyst wrote for it despite instructions to the contrary; tools, not prompts, are the
control. Suite 3 reconciles every numeric agent answer with an audit row of the same hash.

## Edition

| Control | Enterprise edition provides | Standard edition provides | How this layer realises it |
|---|---|---|---|
| Row scope by role | Row access policies | Secure views | `GOV.ENTITLEMENTS` (role, plant or region, or all). On Standard, each table the semantic views read is a secure view in `SEMANTIC_BASE` filtered by `EXISTS … IS_ROLE_IN_SESSION(role_name)`; on Enterprise, `GOV.PLANT_ACCESS` on the same rows. |
| Column rules | Masking policies, tag-based masking | Secure views; tags are available | `GOV.COLUMN_VISIBILITY` (show, masked, null per role and column). Standard: a `CASE` per governed column in the secure view. Enterprise: one masking policy per column with the same rule. Sensitivity tags are set in both. |
| Personas never touch base tables | Same | Same | Semantic views run with owner's rights; personas hold SELECT on their semantic view only. `CONFORMED`, `RAW` and `SEMANTIC_BASE` are denied to them. |
| Lineage | `SNOWFLAKE.CORE.GET_LINEAGE` | Not available | `EXPLAIN_LINEAGE` returns the compiled path from the registry and says which source it used. |
| Time Travel for restore | Up to 90 days | 1 day | Retention is set per environment in `snowflake/environments/*.yaml`. |
| Event table per database | Yes | Account default only | `OPS.SCM_EVENTS_DEFAULT` reads this database's rows from the account event table. |

Standard edition: controls realised as compiled secure views. `render_sql.py` drops the
`-- @enterprise` blocks for an environment whose `edition` is `standard`, so the same commit deploys
to either edition.

## Entitlements as deployed on SCM_DEV

| Role | Row scope |
|---|---|
| SCM_ADMIN, SCM_DEPLOY, EXECUTIVE_ROLE | all plants |
| PLANNING_ROLE, PROCUREMENT_ROLE, LOGISTICS_ROLE | all plants (one scope, so one number) |
| JUDGE_ROLE, SCM_SERVICE_ROLE | all plants |
| EMEA_PLANNING_ROLE | plants in EMEA |

SCM_READER, which every persona inherits, carries no scope: `IS_ROLE_IN_SESSION` sees inherited
roles, so a scope on it would widen every persona.

| Column | Shown to | Others see |
|---|---|---|
| DIM_SUPPLIER.CONTACT_NAME, CONTACT_EMAIL; DIM_CUSTOMER.CONTACT_NAME, CONTACT_EMAIL | SCM_ADMIN, EXECUTIVE_ROLE | `***` |
| DIM_SUPPLIER.BANK_ACCOUNT | SCM_ADMIN, PROCUREMENT_ROLE | `***` |
| FCT_PO_LINE.UNIT_COST, FCT_SHIPMENT.FREIGHT_CHARGE | SCM_ADMIN, PROCUREMENT_ROLE | null |

No semantic view exposes a governed column; the rules protect any future view that does.

## Proof

- `eval/test_governance.py`, account tests: each persona's plants through its semantic view equal
  its registry scope, with EMEA_PLANNING_ROLE seeing only EMEA plants; CONFORMED, RAW and
  SEMANTIC_BASE are denied; every column rule evaluates under each role as `GOV.COLUMN_VISIBILITY`
  says; every view in `SEMANTIC_BASE` is secure.
- `eval/test_persona_consistency.py`: 20 cases × 3 roles, identical rows and hashes
  (`eval/report/persona_account.md`), and every numeric agent answer reconciled to the audit trail.
