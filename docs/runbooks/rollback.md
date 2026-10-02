# Rollback runbook

## Semantic view rollback
Swap grants from V{n+1} back to V{n}:
```sql
USE ROLE SECURITYADMIN;
-- For each view: revoke new, grant old
REVOKE SELECT ON VIEW SCM_PROD.SEMANTIC.SCM_GOVERNED_V2 FROM ROLE SCM_READER;
GRANT SELECT ON VIEW SCM_PROD.SEMANTIC.SCM_GOVERNED_V1 TO ROLE SCM_READER;
-- Repeat for persona views
```

## Service rollback
```bash
make spcs-rollback ENV=prod
```
This reverts to the previous container image tag saved in service_spec.yaml.prev.

## Verification
1. Query the same question; verify the hash matches the pre-deployment state.
2. Check /health returns 200.
3. Review AUDIT.ANSWERS for consistency.
