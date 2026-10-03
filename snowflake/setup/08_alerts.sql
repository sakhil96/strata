-- Alerts for freshness, test failures, evaluation regressions and spend.

USE ROLE ACCOUNTADMIN;
CREATE NOTIFICATION INTEGRATION IF NOT EXISTS SCM_ALERTS
    TYPE = EMAIL ENABLED = TRUE ALLOWED_RECIPIENTS = ('{{ALERT_EMAIL}}');
GRANT USAGE ON INTEGRATION SCM_ALERTS TO ROLE SCM_ADMIN;
GRANT EXECUTE ALERT ON ACCOUNT TO ROLE SCM_ADMIN;

-- Serverless: no warehouse wakes for a check that usually finds nothing. Alerts are created suspended; snowflake/tasks/resume_alerts.sql resumes them once data has landed.
USE ROLE SCM_ADMIN;
USE DATABASE {{DB}};

-- Source freshness alert: fires if any source is stale > 6 hours
CREATE OR REPLACE ALERT {{DB}}.OPS.STALE_SOURCE_ALERT
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (
        SELECT 1 FROM {{DB}}.OPS.FRESHNESS
        WHERE TIMESTAMPDIFF(HOUR, last_loaded_at, CURRENT_TIMESTAMP()) > 6
    ))
    THEN
        CALL SYSTEM$SEND_EMAIL(
            'scm_alerts',
            '{{ALERT_EMAIL}}',
            'SCM Alert: Stale source data in {{ENV}}',
            'One or more source systems have not been refreshed in over 6 hours. Check OPS.FRESHNESS.'
        );

-- dbt test failure alert
CREATE OR REPLACE ALERT {{DB}}.OPS.DBT_TEST_FAILURE_ALERT
    SCHEDULE = '60 MINUTE'
    IF (EXISTS (
        SELECT 1 FROM {{DB}}.OPS.DBT_RUNS
        WHERE status = 'error' AND run_started_at > DATEADD(HOUR, -2, CURRENT_TIMESTAMP())
    ))
    THEN
        CALL SYSTEM$SEND_EMAIL(
            'scm_alerts',
            '{{ALERT_EMAIL}}',
            'SCM Alert: dbt test failure in {{ENV}}',
            'A dbt run has failed. Check OPS.DBT_RUNS for details.'
        );

-- Evaluation regression alert
CREATE OR REPLACE ALERT {{DB}}.OPS.EVAL_REGRESSION_ALERT
    SCHEDULE = 'USING CRON 0 3 * * * UTC'
    IF (EXISTS (
        SELECT 1 FROM {{DB}}.EVAL.EVAL_RUNS
        WHERE pass_rate < 0.90 AND run_at > DATEADD(DAY, -1, CURRENT_TIMESTAMP())
    ))
    THEN
        CALL SYSTEM$SEND_EMAIL(
            'scm_alerts',
            '{{ALERT_EMAIL}}',
            'SCM Alert: Evaluation regression in {{ENV}}',
            'The latest evaluation pass rate dropped below 90%. Check EVAL.EVAL_RUNS.'
        );


-- SLO breach: either latency objective over target in the last 30 days.
CREATE OR REPLACE ALERT {{DB}}.OPS.SLO_BREACH_ALERT
    SCHEDULE = '{{SLO_ALERT_SCHEDULE}}'
    IF (EXISTS (SELECT 1 FROM {{DB}}.OPS.SLO_STATUS WHERE status = 'breached'))
    THEN
        CALL SYSTEM$SEND_EMAIL('scm_alerts', '{{ALERT_EMAIL}}',
            'Strata {{ENV}}: service level breached',
            'An objective in OPS.SLO_STATUS is breached. Open /operations and runbooks/incident.md.');
