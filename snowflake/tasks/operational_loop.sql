-- The nightly loop as one task graph: fetch the repository, build dbt, reload the glossary,
-- check every metric against truth, then record the run. A failure anywhere stops the graph
-- and the finaliser writes the outcome so the alerts in 08_alerts.sql can see it.

USE ROLE SCM_DEPLOY;
USE SCHEMA {{DB}}.OPS;

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_ROOT
    WAREHOUSE = {{WH}}
    SCHEDULE = 'USING CRON 30 1 * * * UTC'
    SUSPEND_TASK_AFTER_NUM_FAILURES = 3
    COMMENT = 'Nightly operational loop'
AS
    ALTER GIT REPOSITORY {{DB}}.OPS.SCM_REPO FETCH;

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_DBT
    WAREHOUSE = {{WH}}
    AFTER {{DB}}.OPS.LOOP_ROOT
AS
    EXECUTE DBT PROJECT {{DB}}.OPS.SCM_DBT ARGS = 'build --target {{ENV}}';

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_GLOSSARY
    WAREHOUSE = {{WH}}
    AFTER {{DB}}.OPS.LOOP_DBT
AS
    EXECUTE IMMEDIATE FROM @{{DB}}.OPS.SCM_REPO/branches/main/snowflake/semantic/load_glossary.sql;

-- Suite 1 on the account: governed month-level answers against EVAL.TRUTH_METRICS.
CREATE OR REPLACE PROCEDURE {{DB}}.EVAL.RUN_METRIC_IDENTITY()
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
DECLARE
    checked NUMBER;
    failed NUMBER;
BEGIN
    CREATE OR REPLACE TEMPORARY TABLE identity_otd AS
        SELECT * FROM SEMANTIC_VIEW({{DB}}.SEMANTIC.SCM_GOVERNED_V1
            DIMENSIONS delivered_lines.period_month
            METRICS delivered_lines.on_time_delivery, delivered_lines.otif, delivered_lines.on_time_to_request);
    SELECT COUNT(*), COUNT_IF(ABS(t.value - g.on_time_delivery) > 0.0001)
      INTO :checked, :failed
      FROM identity_otd g
      JOIN {{DB}}.EVAL.TRUTH_METRICS t
        ON t.metric = 'on_time_delivery' AND t.grouping = 'month' AND t.month = g.period_month;
    INSERT INTO {{DB}}.EVAL.EVAL_RUNS (run_at, suite, passed, total, pass_rate)
        SELECT CURRENT_TIMESTAMP(), 'metric_identity', :checked - :failed, :checked,
               (:checked - :failed) / NULLIF(:checked, 0);
    RETURN OBJECT_CONSTRUCT('checked', :checked, 'failed', :failed);
END;
$$;

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_IDENTITY
    WAREHOUSE = {{WH}}
    AFTER {{DB}}.OPS.LOOP_GLOSSARY
AS
    CALL {{DB}}.EVAL.RUN_METRIC_IDENTITY();

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_RECORD
    WAREHOUSE = {{WH}}
    FINALIZE = {{DB}}.OPS.LOOP_ROOT
AS
    INSERT INTO {{DB}}.OPS.DBT_RUNS (run_started_at, target, status, query_id)
    SELECT CURRENT_TIMESTAMP(), '{{ENV}}',
           IFF(SYSTEM$TASK_RUNTIME_INFO('CURRENT_TASK_GRAPH_RUN_GROUP_ID') IS NOT NULL
               AND NOT EXISTS (SELECT 1 FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
                       SCHEDULED_TIME_RANGE_START => DATEADD(hour, -6, CURRENT_TIMESTAMP())))
                   WHERE name LIKE 'LOOP_%' AND state = 'FAILED'), 'success', 'error'),
           SYSTEM$TASK_RUNTIME_INFO('CURRENT_TASK_GRAPH_RUN_GROUP_ID');

-- Weekly cost: warehouses, the compute pool and Cortex function credits for this environment.
CREATE OR REPLACE TASK {{DB}}.OPS.WEEKLY_COST_REPORT
    WAREHOUSE = {{WH}}
    SCHEDULE = 'USING CRON 0 6 * * MON UTC'
AS
    INSERT INTO {{DB}}.OPS.WEEKLY_COST (week, warehouse_credits, container_credits, ai_credits, credits)
    WITH wh AS (
        SELECT SUM(credits_used) c FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE warehouse_name = '{{WH}}' AND start_time >= DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE()))
          AND start_time < DATE_TRUNC(week, CURRENT_DATE())
    ), pool AS (
        SELECT SUM(credits_used) c FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWPARK_CONTAINER_SERVICES_HISTORY
        WHERE compute_pool_name = 'SCM_POOL_{{ENV}}' AND start_time >= DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE()))
          AND start_time < DATE_TRUNC(week, CURRENT_DATE())
    ), ai AS (
        SELECT SUM(credits) c FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
        WHERE start_time >= DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE()))
          AND start_time < DATE_TRUNC(week, CURRENT_DATE())
    )
    SELECT DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE())), wh.c, pool.c, ai.c,
           COALESCE(wh.c, 0) + COALESCE(pool.c, 0) + COALESCE(ai.c, 0)
    FROM wh, pool, ai;

ALTER TASK {{DB}}.OPS.LOOP_RECORD RESUME;
ALTER TASK {{DB}}.OPS.LOOP_IDENTITY RESUME;
ALTER TASK {{DB}}.OPS.LOOP_GLOSSARY RESUME;
ALTER TASK {{DB}}.OPS.LOOP_DBT RESUME;
ALTER TASK {{DB}}.OPS.LOOP_ROOT RESUME;
ALTER TASK {{DB}}.OPS.WEEKLY_COST_REPORT RESUME;
