-- Operational tables and the status views the API reads. {{DB}} per environment.

USE ROLE ACCOUNTADMIN;
-- The loop runs as SCM_DEPLOY: it executes its own tasks and reads ACCOUNT_USAGE for the weekly cost.
GRANT EXECUTE TASK ON ACCOUNT TO ROLE SCM_DEPLOY;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE SCM_DEPLOY;

USE ROLE SCM_DEPLOY;

CREATE TABLE IF NOT EXISTS {{DB}}.AUDIT.ANSWERS (
    ts TIMESTAMP_LTZ NOT NULL,
    username STRING NOT NULL,
    role_used STRING NOT NULL,
    question STRING,
    metric_names STRING,
    canonical_query VARIANT,
    semantic_query_hash STRING,
    sql_executed STRING,
    result_checksum STRING,
    row_count NUMBER,
    latency_ms NUMBER,
    refusal STRING,
    path STRING
) DATA_RETENTION_TIME_IN_DAYS = {{LONG_RETENTION}}
  CHANGE_TRACKING = TRUE
  COMMENT = 'One row for every governed answer and every refusal';

GRANT INSERT ON TABLE {{DB}}.AUDIT.ANSWERS TO ROLE SCM_READER;

CREATE TABLE IF NOT EXISTS {{DB}}.OPS.LOAD_LOG (
    file_name STRING, table_name STRING, row_count NUMBER, checksum STRING,
    loaded_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(), loaded_by STRING DEFAULT CURRENT_USER()
);
CREATE TABLE IF NOT EXISTS {{DB}}.OPS.FRESHNESS (
    source_system STRING, table_name STRING, last_loaded_at TIMESTAMP_LTZ, row_count NUMBER
);
CREATE TABLE IF NOT EXISTS {{DB}}.OPS.DBT_RUNS (
    run_started_at TIMESTAMP_LTZ, target STRING, status STRING, models_passed NUMBER, tests_failed NUMBER,
    query_id STRING
);
CREATE TABLE IF NOT EXISTS {{DB}}.EVAL.EVAL_RUNS (
    run_at TIMESTAMP_LTZ, suite STRING, passed NUMBER, total NUMBER, pass_rate FLOAT, git_sha STRING, detail VARIANT
);
CREATE TABLE IF NOT EXISTS {{DB}}.OPS.WEEKLY_COST (
    week DATE, warehouse_credits FLOAT, container_credits FLOAT, ai_credits FLOAT, credits FLOAT
);
CREATE TABLE IF NOT EXISTS {{DB}}.SEMANTIC.ACTIVE_VERSION (version NUMBER, promoted_at TIMESTAMP_LTZ);
INSERT INTO {{DB}}.SEMANTIC.ACTIVE_VERSION
    SELECT 1, CURRENT_TIMESTAMP() WHERE NOT EXISTS (SELECT 1 FROM {{DB}}.SEMANTIC.ACTIVE_VERSION);

CREATE OR REPLACE VIEW {{DB}}.OPS.SLO_STATUS AS
WITH recent AS (
    SELECT path, latency_ms FROM {{DB}}.AUDIT.ANSWERS
    WHERE ts > DATEADD(day, -30, CURRENT_TIMESTAMP()) AND refusal IS NULL
)
SELECT 'p95 answer latency through /query' AS name, '≤ 2500 ms' AS target,
       APPROX_PERCENTILE(latency_ms, 0.95)::STRING || ' ms' AS measured,
       CASE WHEN COUNT(*) = 0 THEN 'no_data' WHEN APPROX_PERCENTILE(latency_ms, 0.95) <= 2500 THEN 'met' ELSE 'breached' END AS status,
       'AUDIT.ANSWERS, 30 days, builder path' AS source
FROM recent WHERE path = 'builder'
UNION ALL
SELECT 'p95 answer latency through the agent', '≤ 6 s', APPROX_PERCENTILE(latency_ms, 0.95)::STRING || ' ms',
       CASE WHEN COUNT(*) = 0 THEN 'no_data' WHEN APPROX_PERCENTILE(latency_ms, 0.95) <= 6000 THEN 'met' ELSE 'breached' END, 'AUDIT.ANSWERS, 30 days, agent path'
FROM recent WHERE path = 'agent'
UNION ALL
SELECT 'Evaluation pass rate', '≥ 90%', ROUND(pass_rate * 100, 1)::STRING || '%',
       IFF(pass_rate >= 0.9, 'met', 'breached'), 'EVAL.EVAL_RUNS, latest'
FROM (SELECT pass_rate FROM {{DB}}.EVAL.EVAL_RUNS WHERE suite = 'all' ORDER BY run_at DESC LIMIT 1);

-- ALERT_HISTORY and SHOW ALERTS answer only the alert's owner, so the readers' view of the alerts
-- is a procedure that runs as that owner: SHOW ALERTS for started or suspended, the history for
-- the last outcome. Timestamps come back as text, the way the page shows them.
USE ROLE SCM_ADMIN;
DROP VIEW IF EXISTS {{DB}}.OPS.ALERT_STATUS;
CREATE OR REPLACE PROCEDURE {{DB}}.OPS.ALERT_STATUS()
RETURNS TABLE (name STRING, schedule STRING, state STRING, last_outcome STRING, last_run STRING, last_fired STRING)
LANGUAGE SQL
EXECUTE AS OWNER
AS
$$
DECLARE
    result RESULTSET;
BEGIN
    SHOW ALERTS IN SCHEMA {{DB}}.OPS;
    result := (
        WITH shown AS (
            SELECT "name" AS name, "schedule" AS schedule, "state" AS state FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
        ), history AS (
            SELECT name, MAX_BY(state, completed_time) AS last_outcome, MAX(completed_time) AS last_run,
                   MAX(IFF(state = 'TRIGGERED', completed_time, NULL)) AS last_fired
            FROM TABLE({{DB}}.INFORMATION_SCHEMA.ALERT_HISTORY(
                SCHEDULED_TIME_RANGE_START => DATEADD(hour, -167, CURRENT_TIMESTAMP()),
                SCHEDULED_TIME_RANGE_END => CURRENT_TIMESTAMP()))
            WHERE database_name = '{{DB}}' AND schema_name = 'OPS' AND completed_time IS NOT NULL
            GROUP BY name
        )
        SELECT s.name::STRING, s.schedule::STRING, s.state::STRING, h.last_outcome::STRING,
               h.last_run::STRING, h.last_fired::STRING
        FROM shown s LEFT JOIN history h USING (name)
        ORDER BY s.name
    );
    RETURN TABLE(result);
END;
$$;
GRANT USAGE ON PROCEDURE {{DB}}.OPS.ALERT_STATUS() TO ROLE SCM_READER;
USE ROLE SCM_DEPLOY;

GRANT SELECT ON VIEW {{DB}}.OPS.SLO_STATUS TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.OPS.FRESHNESS TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.OPS.DBT_RUNS TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.OPS.WEEKLY_COST TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.EVAL.EVAL_RUNS TO ROLE SCM_READER;
