-- Alerts for freshness, test failures, evaluation regressions and spend.

USE ROLE SCM_ADMIN;
USE DATABASE {{DB}};

-- Source freshness alert: fires if any source is stale > 6 hours
CREATE OR REPLACE ALERT {{DB}}.OPS.STALE_SOURCE_ALERT
    WAREHOUSE = SCM_WH_{{ENV}}
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (
        SELECT 1 FROM {{DB}}.OPS.FRESHNESS
        WHERE TIMESTAMPDIFF(HOUR, last_loaded_at, CURRENT_TIMESTAMP()) > 6
    ))
    THEN
        CALL SYSTEM$SEND_EMAIL(
            'scm_alerts',
            '42152708+sakhil96@users.noreply.github.com',
            'SCM Alert: Stale source data in {{ENV}}',
            'One or more source systems have not been refreshed in over 6 hours. Check OPS.FRESHNESS.'
        );

-- dbt test failure alert
CREATE OR REPLACE ALERT {{DB}}.OPS.DBT_TEST_FAILURE_ALERT
    WAREHOUSE = SCM_WH_{{ENV}}
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (
        SELECT 1 FROM {{DB}}.OPS.DBT_RUNS
        WHERE status = 'error' AND run_started_at > DATEADD(HOUR, -2, CURRENT_TIMESTAMP())
    ))
    THEN
        CALL SYSTEM$SEND_EMAIL(
            'scm_alerts',
            '42152708+sakhil96@users.noreply.github.com',
            'SCM Alert: dbt test failure in {{ENV}}',
            'A dbt run has failed. Check OPS.DBT_RUNS for details.'
        );

-- Evaluation regression alert
CREATE OR REPLACE ALERT {{DB}}.OPS.EVAL_REGRESSION_ALERT
    WAREHOUSE = SCM_WH_{{ENV}}
    SCHEDULE = 'USING CRON 0 3 * * * UTC'
    IF (EXISTS (
        SELECT 1 FROM {{DB}}.EVAL.EVAL_RUNS
        WHERE pass_rate < 0.90 AND run_at > DATEADD(DAY, -1, CURRENT_TIMESTAMP())
    ))
    THEN
        CALL SYSTEM$SEND_EMAIL(
            'scm_alerts',
            '42152708+sakhil96@users.noreply.github.com',
            'SCM Alert: Evaluation regression in {{ENV}}',
            'The latest evaluation pass rate dropped below 90%. Check EVAL.EVAL_RUNS.'
        );

-- Resume alerts
ALTER ALERT {{DB}}.OPS.STALE_SOURCE_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.DBT_TEST_FAILURE_ALERT RESUME;
ALTER ALERT {{DB}}.OPS.EVAL_REGRESSION_ALERT RESUME;
