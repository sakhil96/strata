-- Governed procedures for one environment. {{DB}} is SCM_DEV, SCM_TEST or SCM_PROD.
-- Code comes from {{CODE_STAGE}}: the Git repository object where one exists, otherwise the
-- committed files PUT to OPS.ARTEFACTS/code by scripts/stage_code.py.
-- semantic.py reads metrics.yaml from beside itself; both are imported from the same commit.

USE ROLE SCM_DEPLOY;
USE SCHEMA {{DB}}.AGENT;

-- AUDIT.ANSWERS is created by setup/10_ops.sql; the SLO views read it.

DROP PROCEDURE IF EXISTS {{DB}}.AGENT.GOVERNED_QUERY(STRING, ARRAY, ARRAY, OBJECT, ARRAY, STRING);
CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.GOVERNED_QUERY(VIEW STRING, QUERY STRING, QUESTION STRING DEFAULT '')
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'snowflake-telemetry-python', 'pyyaml')
IMPORTS = (
    '{{CODE_STAGE}}/ontology/semantic.py',
    '{{CODE_STAGE}}/ontology/metrics.yaml',
    '{{CODE_STAGE}}/snowflake/procs/governed_query.py',
    '{{CODE_STAGE}}/snowflake/procs/explain_lineage.py'
)
HANDLER = 'governed_query.run'
COMMENT = 'The only path from a question to a number; writes AUDIT.ANSWERS'
EXECUTE AS CALLER;

CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.DESCRIBE_METRIC(NAME STRING)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'pyyaml')
IMPORTS = (
    '{{CODE_STAGE}}/ontology/semantic.py',
    '{{CODE_STAGE}}/ontology/metrics.yaml',
    '{{CODE_STAGE}}/snowflake/procs/describe_metric.py'
)
HANDLER = 'describe_metric.run'
EXECUTE AS CALLER;

CREATE OR REPLACE PROCEDURE {{DB}}.AGENT.EXPLAIN_LINEAGE(METRIC STRING)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'pyyaml')
IMPORTS = (
    '{{CODE_STAGE}}/ontology/semantic.py',
    '{{CODE_STAGE}}/ontology/metrics.yaml',
    '{{CODE_STAGE}}/snowflake/procs/explain_lineage.py'
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

GRANT USAGE ON PROCEDURE {{DB}}.AGENT.GOVERNED_QUERY(STRING, STRING, STRING) TO ROLE SCM_READER;
GRANT USAGE ON PROCEDURE {{DB}}.AGENT.DESCRIBE_METRIC(STRING) TO ROLE SCM_READER;
GRANT USAGE ON PROCEDURE {{DB}}.AGENT.EXPLAIN_LINEAGE(STRING) TO ROLE SCM_READER;
GRANT USAGE ON PROCEDURE {{DB}}.AGENT.RECORD_REFUSAL(STRING, STRING) TO ROLE SCM_READER;
