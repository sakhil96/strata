-- The nightly loop as one task graph: refresh the code, build dbt, reapply the sensitivity tags
-- the build replaced, reload the glossary, check metrics against truth, then record the run. A
-- failure anywhere stops the graph and the finaliser writes the outcome for 08_alerts.sql.
-- Created suspended; snowflake/tasks/resume_loop.sql resumes it once one manual run is green.

USE ROLE SCM_DEPLOY;
USE SCHEMA {{DB}}.OPS;

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_ROOT
    WAREHOUSE = {{WH}}
    SCHEDULE = 'USING CRON 30 1 * * * UTC'
    SUSPEND_TASK_AFTER_NUM_FAILURES = 3
    COMMENT = 'Nightly operational loop'
AS
    {{CODE_REFRESH}};

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_DBT
    WAREHOUSE = {{WH}}
    AFTER {{DB}}.OPS.LOOP_ROOT
AS
    -- dim_document is excluded: its AI_CLASSIFY and AI_FILTER columns cost about 5 credits a
    -- rebuild and change only when documents are reloaded, which rebuilds it explicitly.
    EXECUTE DBT PROJECT {{DB}}.OPS.SCM_DBT ARGS = 'build --exclude dim_document --target {{ENV_NAME}}';

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_TAGS
    WAREHOUSE = {{WH}}
    AFTER {{DB}}.OPS.LOOP_DBT
AS
    EXECUTE IMMEDIATE FROM '{{CODE_STAGE}}/snowflake/policies/tags.sql';

CREATE OR REPLACE TASK {{DB}}.OPS.LOOP_GLOSSARY
    WAREHOUSE = {{WH}}
    AFTER {{DB}}.OPS.LOOP_TAGS
AS
    EXECUTE IMMEDIATE FROM '{{CODE_STAGE}}/snowflake/semantic/load_glossary.sql';

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
               AND NOT EXISTS (SELECT 1 FROM TABLE({{DB}}.INFORMATION_SCHEMA.TASK_HISTORY(
                       SCHEDULED_TIME_RANGE_START => DATEADD(hour, -6, CURRENT_TIMESTAMP())))
                   WHERE name LIKE 'LOOP_%' AND state = 'FAILED'), 'success', 'error'),
           SYSTEM$TASK_RUNTIME_INFO('CURRENT_TASK_GRAPH_RUN_GROUP_ID');

-- Weekly cost: warehouses, the compute pool and Cortex function credits for this environment.
-- Daily, so this week's row is week to date and last week's row closes on Monday's run.
CREATE OR REPLACE TASK {{DB}}.OPS.WEEKLY_COST_REPORT
    WAREHOUSE = {{WH}}
    SCHEDULE = 'USING CRON 0 6 * * * UTC'
AS
    MERGE INTO {{DB}}.OPS.WEEKLY_COST t
    USING (
        WITH weeks AS (
            SELECT DATE_TRUNC(week, CURRENT_DATE()) AS week
            UNION ALL SELECT DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE()))
        ), wh AS (
            SELECT DATE_TRUNC(week, start_time)::DATE week, SUM(credits_used) c
            FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
            WHERE warehouse_name = '{{WH}}' AND start_time >= DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE()))
            GROUP BY 1
        ), pool AS (
            SELECT DATE_TRUNC(week, start_time)::DATE week, SUM(credits_used) c
            FROM SNOWFLAKE.ACCOUNT_USAGE.SNOWPARK_CONTAINER_SERVICES_HISTORY
            WHERE compute_pool_name = 'SCM_POOL_{{ENV}}' AND start_time >= DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE()))
            GROUP BY 1
        ), ai AS (
            SELECT DATE_TRUNC(week, start_time)::DATE week, SUM(token_credits) c
            FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_FUNCTIONS_USAGE_HISTORY
            WHERE start_time >= DATEADD(week, -1, DATE_TRUNC(week, CURRENT_DATE()))
            GROUP BY 1
        )
        SELECT w.week, wh.c AS warehouse_credits, pool.c AS container_credits, ai.c AS ai_credits,
               COALESCE(wh.c, 0) + COALESCE(pool.c, 0) + COALESCE(ai.c, 0) AS credits
        FROM weeks w LEFT JOIN wh USING (week) LEFT JOIN pool USING (week) LEFT JOIN ai USING (week)
    ) s ON t.week = s.week
    WHEN MATCHED THEN UPDATE SET warehouse_credits = s.warehouse_credits, container_credits = s.container_credits,
                                 ai_credits = s.ai_credits, credits = s.credits
    WHEN NOT MATCHED THEN INSERT (week, warehouse_credits, container_credits, ai_credits, credits)
                          VALUES (s.week, s.warehouse_credits, s.container_credits, s.ai_credits, s.credits);
