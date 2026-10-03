-- Resume the alerts after the first load, so they judge real freshness rather than an empty table.
-- On a one-shot DEV load the stale-source alert fires hourly from six hours after the load.
USE ROLE SCM_ADMIN;
ALTER ALERT {{DB}}.OPS.STALE_SOURCE_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.DBT_TEST_FAILURE_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.EVAL_REGRESSION_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.SLO_BREACH_ALERT RESUME;
