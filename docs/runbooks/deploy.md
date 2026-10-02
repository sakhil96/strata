# Deploy runbook

## Pre-deploy checklist
1. All CI checks pass on the branch.
2. Evaluation suites 1-7 green against SCM_TEST.
3. Semantic view YAML round-trip verified.
4. Grants snapshot diff reviewed.

## Deploy to TEST
```bash
make compile ENV=test VERSION=2
snow sql -f snowflake/semantic/deploy.sql  # substitute {{DB}}=SCM_TEST
snow sql -f snowflake/semantic/versioning.sql
make eval ENV=test
```

## Deploy to PROD
```bash
# Triggered via GitHub Actions deploy.yml workflow_dispatch
# Or manually:
make compile ENV=prod VERSION=2
snow sql -f snowflake/semantic/deploy.sql  # {{DB}}=SCM_PROD
snow sql -f snowflake/semantic/versioning.sql
```

## Post-deploy verification
1. Spot-check /ask with a known question.
2. Verify /query returns the same hash as TEST.
3. Check /health and /live probes.
4. Review AUDIT.ANSWERS for the first few answers.
