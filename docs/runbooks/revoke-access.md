# Revoke access runbook

## Emergency access revocation
When a user or service account must be immediately locked out.

## Steps
1. Disable the user:
   ```sql
   ALTER USER <username> SET DISABLED = TRUE;
   ```

2. Revoke all role grants:
   ```sql
   REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA SCM_PROD.CONFORMED FROM ROLE <role>;
   ```

3. Kill active sessions:
   ```sql
   SELECT SYSTEM$ABORT_SESSION(<session_id>);
   ```

4. Review audit trail:
   ```sql
   SELECT * FROM SCM_PROD.AUDIT.ANSWERS WHERE username = '<username>' ORDER BY ts DESC LIMIT 100;
   ```

5. Update network policy if the source IP should be blocked.

6. Record the revocation in an incident report.
