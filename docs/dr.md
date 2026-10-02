# Disaster Recovery

## RPO and RTO targets
- RPO (Recovery Point Objective): 24 hours for CONFORMED and AUDIT data (Time Travel).
- RTO (Recovery Time Objective): 4 hours for full service restoration.

## Time Travel
- CONFORMED and AUDIT schemas: DATA_RETENTION_TIME_IN_DAYS = 90.
- Other schemas: 14 days (database default).

## Recovery procedures

### Table-level restore
```sql
CREATE TABLE CONFORMED.FCT_SALES_ORDER_LINE_RESTORED
  CLONE CONFORMED.FCT_SALES_ORDER_LINE
  AT (TIMESTAMP => '2026-10-01 00:00:00'::TIMESTAMP_NTZ);
```

### Schema-level restore
```sql
CREATE SCHEMA SCM_PROD.CONFORMED_RESTORED
  CLONE SCM_PROD.CONFORMED
  AT (TIMESTAMP => '2026-10-01 00:00:00'::TIMESTAMP_NTZ);
```

### UNDROP
```sql
UNDROP TABLE SCM_PROD.CONFORMED.FCT_SALES_ORDER_LINE;
```

## Replication (Business Critical Edition)
- Failover group covering SCM_PROD database, roles and integrations.
- Secondary account in a different region.
- Failover tested quarterly.

## Semantic view rollback
- Swap grants from V{n+1} back to V{n} using versioning.sql.
- Previous version kept for one release cycle.

## Service rollback
- `make spcs-rollback` reverts to the previous container image tag.
- Previous service spec saved as service_spec.yaml.prev.
