# STRATA — Supply Chain Ontology & Governed Semantic Views

STRATA is a supply chain metrics application on Snowflake. The ontology is authored once in LinkML
YAML (`ontology/`) and compiled into five Snowflake semantic views, dbt models with tests, a glossary
with lineage, an Apache Ossie interchange model and a Cube fallback. A Cortex Agent reads the
question; the number comes only from `GOVERNED_QUERY`, run as the asker's persona on that persona's
semantic view, with one audit row per answer. Planning, procurement, logistics and executive users
asking the same question in their own words get the same number, the same definition and the same
query hash, and each sees only the rows and columns their role allows.

| | |
|---|---|
| Live app (Snowflake account sign-in) | https://mbloac-dzvlnoz-zv32033.snowflakecomputing.app |
| Public mirror (recorded demo data, no sign-in) | https://strata-wine-one.vercel.app |
| Functional overview | [docs/overview.md](docs/overview.md) |
| Evaluator guide and access | [docs/how-to-evaluate.md](docs/how-to-evaluate.md) |

## Five minutes for an evaluator

1. **Ask** — open the live app (first sign-in: [Evaluator access](docs/how-to-evaluate.md#evaluator-access)),
   choose a persona on the dial and press *What is on-time delivery for FY2026?* The ledger on the
   right shows the governed definition, the role and semantic view it ran under, the query hash and
   the SQL.
2. **Switch persona** — ask again as Logistics, then as Planning, EMEA. The number and hash hold for
   the global personas; EMEA answers on its own plants only.
3. **Compare** — three roles, three phrasings, one hash.
4. **Before and after** — three legacy on-time numbers computed on RAW against the governed one.
5. **Governance** — the agent's tools (three governed procedures and Cortex Search over notes; no
   SQL tool), the grants, and your own questions in the audit trail.

No account? The mirror replays the same pages from recorded answers and says so on every page.

## Architecture

```
ontology.yaml → compile.py → semantic views + dbt + glossary + Ossie + Cube
4 source systems → RAW → STAGING → CONFORMED → SEMANTIC_BASE (secure views) → SEMANTIC
Cortex Agent → GOVERNED_QUERY (caller's rights) → SEMANTIC_VIEW() → AUDIT.ANSWERS
FastAPI + Next.js → SPCS service → public endpoint, Snowflake sign-in
```

See `docs/architecture.md` for the full diagram and `docs/DECISIONS.md` for why.

## Quick start without an account

Python 3.11 and Node 22.

```bash
uv venv .venv --python 3.11 && uv pip install -r requirements-dev.lock
cd web && npm ci && cd ..
make local-demo PY=.venv/bin/python   # data, dbt on DuckDB, compile, web build, API on :8000
```

Open http://127.0.0.1:8000. The local engine uses the same canonicaliser, query hash and SQL
renderer as the Snowflake procedures, so hashes match what the account returns.

## Deploying to a Snowflake account

```bash
make setup ENV=dev CONN=<connection>     # roles, schemas, policies, monitors, alerts
make data load ENV=dev CONN=<connection> # deterministic source files, staged and loaded
make deploy ENV=dev CONN=<connection>    # compiled views, procedures, agent
make spcs-build && make spcs-deploy ENV=dev CONN=<connection>
```

## Environments

| Environment | Database  | Warehouse    | Role        |
|-------------|-----------|--------------|-------------|
| dev         | SCM_DEV   | SCM_WH_DEV   | SCM_ADMIN   |
| test        | SCM_TEST  | SCM_WH_TEST  | SCM_DEPLOY  |
| prod        | SCM_PROD  | SCM_WH_PROD  | SCM_DEPLOY  |

Changes reach PROD only through `deploy.yml` after all evaluation gates pass.

## Governed metrics

| Metric | Type | Grain | SCOR |
|--------|------|-------|------|
| on_time_delivery | ratio | sales_order_line | RL.1.1 |
| otif | ratio | sales_order_line | RL.1.1 |
| unit_fill_rate | ratio | sales_order_line | RL.2.3 |
| days_of_inventory | ratio | storage_location_part | AM.2.2 |
| landed_cost_per_unit | weighted_average | purchase_order_line | CO.2.1 |
| supplier_lead_time_days | percentile | purchase_order_line | RS.2.1 |
| inventory_turns | ratio | storage_location_part | AM.2.1 |
| stockout_rate | ratio | storage_location_part | RL.3.35 |
| freight_cost_per_unit | weighted_average | shipment_line | CO.2.4 |
| order_fulfilment_cycle_days | percentile | sales_order_line | RS.1.1 |

All ratios are ratios of sums at the requested grouping. Never averages of ratios.

## Evaluation suites

1. Metric identity (truth table match within tolerance)
2. NL accuracy (agent resolution >= 90%)
3. Persona consistency (identical hash across 3 roles, 20/20)
4. Governance (tools, policies, lineage, round-trip, grants, audit)
5. Resilience (probes, builder without model, timeouts, rollback)
6. Front end (Playwright e2e, axe, security headers, banned words)
7. Supply chain of the software (dependency audit, image scan, SBOM)

## Design principles

1. One ontology, many targets. Edit the registry, not the output.
2. Governed by default. No raw SQL in the agent. Every answer audited.
3. Identical answers. Same hash, same number, every persona.
4. Ratios of sums. Never average pre-computed ratios.
5. The AI is a component, not the application.

## Licence

Apache 2.0. See `LICENSE`.

Fonts under SIL Open Font License. Reference data: public domain or public data.
See `THIRD_PARTY_NOTICES.md` for details.
