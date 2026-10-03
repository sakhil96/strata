-- Resume the alerts after the first load, so they judge real freshness rather than an empty table.
-- The stale-source alert stays suspended on the one-shot DEV load (Standard), where it would fire hourly.
USE ROLE SCM_ADMIN;
-- @enterprise
ALTER ALERT {{DB}}.OPS.STALE_SOURCE_ALERT RESUME;
-- @end
ALTER ALERT {{DB}}.OPS.DBT_TEST_FAILURE_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.EVAL_REGRESSION_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.SLO_BREACH_ALERT RESUME;
