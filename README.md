# STRATA — Supply Chain Ontology & Governed Semantic Views

An enterprise application where a supply chain ontology is authored once (LinkML YAML) and
compiled into Snowflake semantic views, dbt models with tests, a glossary with lineage, an
Apache Ossie interchange model and a Cube fallback. A Cortex Agent answers cross-domain
questions only through governed procedures over the semantic views, so planning, procurement
and logistics personas get identical answers to the same question.

## Architecture

```
ontology.yaml → compile.py → semantic views + dbt + glossary + Ossie + Cube
4 source systems → RAW → STAGING → CONFORMED → SEMANTIC
Cortex Agent → GOVERNED_QUERY → SEMANTIC_VIEW() → AUDIT.ANSWERS
FastAPI + Next.js → SPCS container → Snowflake login
```

See `docs/architecture.md` for the full diagram.

## Quick start

```bash
# 1. Configure Snowflake connection
snow connection add scm_dev --account <account> --user <user> --authenticator externalbrowser

# 2. Set up the environment
make setup ENV=dev        # Run setup SQL (substitute {{DB}} and {{ENV}})

# 3. Generate and load data
make data                 # Generate deterministic test data
make load ENV=dev         # Stage and COPY INTO Snowflake

# 4. Compile the ontology
make compile ENV=dev      # Generate semantic views, dbt schema, glossary, etc.

# 5. Deploy semantic views
make deploy ENV=dev       # SYSTEM$CREATE_SEMANTIC_VIEW_FROM_YAML + grant versioning

# 6. Run locally
cd api && uvicorn main:app --reload
cd web && npm run dev
```

## Local fallback (no Snowflake)

```bash
make local-demo           # DuckDB + dbt-core + Cube from the same ontology
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
