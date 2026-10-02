# Operations

## Escalation contacts
- On-call: Data Platform team (PagerDuty rotation).
- Metric questions: Supply Chain Analytics Lead (steward).
- Security incidents: Security team + SCM_ADMIN.

## Monitoring
- Source freshness: OPS.FRESHNESS, alert at > 6 hours stale.
- dbt failures: OPS.DBT_RUNS, alert on status = 'error'.
- Evaluation regression: EVAL.EVAL_RUNS, alert if pass_rate < 90%.
- Resource monitors: SCM_DEV_MONITOR, SCM_TEST_MONITOR, SCM_PROD_MONITOR.
- Service health: /health and /live probes.
- Event table: OPS.SCM_EVENTS for structured telemetry.

## Routine tasks
- Weekly: cost review (resource monitor report + compute pool usage).
- Weekly: access review (SHOW GRANTS diff against committed snapshot).
- Nightly: evaluation run against SCM_TEST via Cortex Code automation.
- Quarterly: key rotation per runbooks/rotate-keys.md.
- Quarterly: DR failover test.

## Deployment
- All changes through Git + CI. See .github/workflows/deploy.yml.
- Semantic views versioned: deploy V{n+1} beside V{n}, swap grants, keep V{n} for rollback.
- SPCS: build image, push to image repo, update service spec, test probes, promote.
