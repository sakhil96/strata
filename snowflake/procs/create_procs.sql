-- Governed procedures for one environment. {{DB}} is SCM_DEV, SCM_TEST or SCM_PROD.
-- Code comes from the Git repository object, so what runs is what is committed.
-- semantic.py reads metrics.yaml from beside itself; both are imported from the same commit.

USE ROLE SCM_DEPLOY;
USE SCHEMA {{DB}}.AGENT;

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
) DATA_RETENTION_TIME_IN_DAYS = 90
  CHANGE_TRACKING = TRUE
  COMMENT = 'One row for every governed answer and every refusal';

GRANT INSERT ON TABLE {{DB}}.AUDIT.ANSWERS TO ROLE SCM_READER;

CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.GOVERNED_QUERY(
    VIEW STRING, METRICS ARRAY, DIMENSIONS ARRAY, TIME_WINDOW OBJECT, FILTERS ARRAY, QUESTION STRING DEFAULT ''
)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'snowflake-telemetry-python', 'pyyaml')
IMPORTS = (
    '@{{DB}}.OPS.SCM_REPO/branches/main/ontology/semantic.py',
    '@{{DB}}.OPS.SCM_REPO/branches/main/ontology/metrics.yaml',
    '@{{DB}}.OPS.SCM_REPO/branches/main/snowflake/procs/governed_query.py',
    '@{{DB}}.OPS.SCM_REPO/branches/main/snowflake/procs/explain_lineage.py'
)
HANDLER = 'governed_query.run'
EXECUTE AS CALLER
COMMENT = 'The only path from a question to a number; writes AUDIT.ANSWERS';

CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.DESCRIBE_METRIC(NAME STRING)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'pyyaml')
IMPORTS = (
    '@{{DB}}.OPS.SCM_REPO/branches/main/ontology/semantic.py',
    '@{{DB}}.OPS.SCM_REPO/branches/main/ontology/metrics.yaml',
    '@{{DB}}.OPS.SCM_REPO/branches/main/snowflake/procs/describe_metric.py'
)
HANDLER = 'describe_metric.run'
EXECUTE AS CALLER;

CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.EXPLAIN_LINEAGE(METRIC STRING)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'pyyaml')
IMPORTS = (
    '@{{DB}}.OPS.SCM_REPO/branches/main/ontology/semantic.py',
    '@{{DB}}.OPS.SCM_REPO/branches/main/ontology/metrics.yaml',
    '@{{DB}}.OPS.SCM_REPO/branches/main/snowflake/procs/explain_lineage.py'
)
HANDLER = 'explain_lineage.run'
EXECUTE AS CALLER;

CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.RECORD_REFUSAL(QUESTION STRING, REASON STRING)
RETURNS VARIANT
LANGUAGE SQL
EXECUTE AS CALLER
AS
$$
BEGIN
    INSERT INTO AUDIT.ANSWERS (ts, username, role_used, question, refusal, path)
    SELECT CURRENT_TIMESTAMP(), CURRENT_USER(), CURRENT_ROLE(), :QUESTION, :REASON, 'api';
    RETURN OBJECT_CONSTRUCT('recorded', TRUE);
END;
$$;

GRANT USAGE ON PROCEDURE {{DB}}.AGENT.GOVERNED_QUERY(STRING, ARRAY, ARRAY, OBJECT, ARRAY, STRING) TO ROLE SCM_READER;
GRANT USAGE ON PROCEDURE {{DB}}.AGENT.DESCRIBE_METRIC(STRING) TO ROLE SCM_READER;
GRANT USAGE ON PROCEDURE {{DB}}.AGENT.EXPLAIN_LINEAGE(STRING) TO ROLE SCM_READER;
GRANT USAGE ON PROCEDURE {{DB}}.AGENT.RECORD_REFUSAL(STRING, STRING) TO ROLE SCM_READER;
