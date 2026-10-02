# Incident response runbook

## Severity levels
- **P1**: Service down, data breach, or production data corruption.
- **P2**: Degraded service (agent unavailable, metrics returning errors).
- **P3**: Non-critical (stale data, failed evaluation, test regression).

## Response flow
1. **Detect**: alert fires, user report, or monitoring dashboard.
2. **Triage**: identify severity, affected scope, and blast radius.
3. **Contain**: disable the affected component (suspend service, revoke access).
4. **Investigate**: check event table, audit trail, dbt run logs, service logs.
5. **Resolve**: deploy fix or rollback per the appropriate runbook.
6. **Communicate**: notify affected users and stakeholders.
7. **Post-mortem**: document root cause, timeline, and prevention measures.

## Escalation
- P1: immediate page to on-call + SCM_ADMIN + security team.
- P2: notify on-call within 30 minutes.
- P3: addressed in next business day.
