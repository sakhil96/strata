-- Operational tables and the status views the API reads. {{DB}} per environment.

USE ROLE SCM_DEPLOY;

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
SELECT 'p95 answer latency through /query' AS name, '≤ 1500 ms' AS target,
       APPROX_PERCENTILE(latency_ms, 0.95)::STRING || ' ms' AS measured,
       IFF(APPROX_PERCENTILE(latency_ms, 0.95) <= 1500, 'met', 'breached') AS status,
       'AUDIT.ANSWERS, 30 days, builder path' AS source
FROM recent WHERE path = 'builder'
UNION ALL
SELECT 'p95 answer latency through the agent', '≤ 6 s', APPROX_PERCENTILE(latency_ms, 0.95)::STRING || ' ms',
       IFF(APPROX_PERCENTILE(latency_ms, 0.95) <= 6000, 'met', 'breached'), 'AUDIT.ANSWERS, 30 days, agent path'
FROM recent WHERE path = 'agent'
UNION ALL
SELECT 'Evaluation pass rate', '≥ 90%', ROUND(pass_rate * 100, 1)::STRING || '%',
       IFF(pass_rate >= 0.9, 'met', 'breached'), 'EVAL.EVAL_RUNS, latest'
FROM (SELECT pass_rate FROM {{DB}}.EVAL.EVAL_RUNS WHERE suite = 'all' ORDER BY run_at DESC LIMIT 1);

CREATE OR REPLACE VIEW {{DB}}.OPS.ALERT_STATUS AS
SELECT name, schedule, MAX(IFF(state = 'TRIGGERED', completed_time, NULL)) AS last_fired, MAX(state) AS state
FROM TABLE({{DB}}.INFORMATION_SCHEMA.ALERT_HISTORY(SCHEDULED_TIME_RANGE_START => DATEADD(day, -7, CURRENT_TIMESTAMP())))
GROUP BY name, schedule;

GRANT SELECT ON VIEW {{DB}}.OPS.SLO_STATUS TO ROLE SCM_READER;
GRANT SELECT ON VIEW {{DB}}.OPS.ALERT_STATUS TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.OPS.FRESHNESS TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.OPS.DBT_RUNS TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.OPS.WEEKLY_COST TO ROLE SCM_READER;
GRANT SELECT ON TABLE {{DB}}.EVAL.EVAL_RUNS TO ROLE SCM_READER;
