# Restore runbook

## Table-level restore from Time Travel
```sql
-- Restore to a specific point in time
CREATE OR REPLACE TABLE SCM_PROD.CONFORMED.FCT_SALES_ORDER_LINE
  CLONE SCM_PROD.CONFORMED.FCT_SALES_ORDER_LINE
  AT (TIMESTAMP => '<timestamp>'::TIMESTAMP_NTZ);
```

## Schema-level restore
```sql
CREATE OR REPLACE SCHEMA SCM_PROD.CONFORMED
  CLONE SCM_PROD.CONFORMED
  AT (TIMESTAMP => '<timestamp>'::TIMESTAMP_NTZ);
```

## UNDROP (accidental deletion)
```sql
UNDROP TABLE SCM_PROD.CONFORMED.FCT_SALES_ORDER_LINE;
UNDROP SCHEMA SCM_PROD.CONFORMED;
UNDROP DATABASE SCM_PROD;
```

## Full environment rebuild
```bash
make setup ENV=prod
make data
make load ENV=prod
make compile ENV=prod
make deploy ENV=prod
```

## Verification
1. Row counts match expectations.
2. A governed query returns the expected hash.
3. Evaluation suites pass.
