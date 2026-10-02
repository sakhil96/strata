# Architecture

## Layers

```
┌─────────────────────────────────────────────────────────┐
│  STRATA front end (Next.js static export)                │
│  PersonaDial · Builder · Ledger · Convergence · Charts   │
├─────────────────────────────────────────────────────────┤
│  FastAPI  /ask  /query  /glossary  /lineage  /audit      │
│  Security: CSP, HSTS, rate limiting, Pydantic validation │
├─────────────────────────────────────────────────────────┤
│  Cortex Agent (3 tools, no SQL, pinned model)            │
│  GOVERNED_QUERY → SEMANTIC_VIEW() → AUDIT.ANSWERS        │
├─────────────────────────────────────────────────────────┤
│  Semantic Views: SCM_GOVERNED, PLANNING_SV, etc.         │
│  Masking policies · Row access policies · Tags           │
├─────────────────────────────────────────────────────────┤
│  CONFORMED: dim_supplier, fct_sales_order_line, etc.     │
│  dbt project (Snowflake + DuckDB targets)                │
├─────────────────────────────────────────────────────────┤
│  STAGING: crosswalk, dedup, type resolution              │
├─────────────────────────────────────────────────────────┤
│  RAW: 4 source systems (ERP, TMS, Portal, IoT)          │
│  Parquet on internal stages                              │
├─────────────────────────────────────────────────────────┤
│  Ontology: ontology.yaml + metrics.yaml → compile.py     │
│  Targets: semantic views, dbt, glossary, Ossie, Cube     │
└─────────────────────────────────────────────────────────┘
```

## Data flow

1. `generate.py` creates four source systems as Parquet with injected inconsistencies.
2. `load.py` stages and COPY INTO RAW tables with load log and freshness tracking.
3. dbt staging models resolve crosswalk, date field names, UOM, and timezone inconsistencies.
4. dbt conformed models produce clean dimensions and facts.
5. `compile.py` reads the ontology and registry, generates semantic view YAML, dbt schema,
   glossary, Ossie model and Cube views.
6. Semantic views deployed with versioning (`_V1`, `_V2`); grants swapped atomically.
7. The Cortex Agent uses GOVERNED_QUERY, DESCRIBE_METRIC and EXPLAIN_LINEAGE — no SQL tool.
8. FastAPI serves /ask (agent) and /query (builder, no model needed).
9. SPCS container runs both API and Next.js static export behind a public endpoint.

## Security

- Functional role hierarchy: SCM_ADMIN > SCM_DEPLOY > persona roles > SCM_READER.
- Row access policies on conformed facts.
- Tag-based masking policies on CONFIDENTIAL and RESTRICTED columns.
- Network policies restrict the account to known CIDRs.
- Resource monitors with notify and suspend thresholds.
- Event table for OpenTelemetry telemetry.
- Alerts for freshness, test failures, evaluation regression and spend.
- SPCS: readiness/liveness probes, secrets as snowflakeSecret references, no host networking.
