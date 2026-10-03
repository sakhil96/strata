-- Resume the alerts after the first load, so they judge real freshness rather than an empty table.
-- DEV loads its sources once, so its environment file keeps the stale-source alert suspended.
USE ROLE SCM_ADMIN;
ALTER ALERT {{DB}}.OPS.STALE_SOURCE_ALERT {{STALE_SOURCE_ALERT}};
ALTER ALERT {{DB}}.OPS.DBT_TEST_FAILURE_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.EVAL_REGRESSION_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.SLO_BREACH_ALERT RESUME;
