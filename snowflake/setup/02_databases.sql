-- Databases and schemas for each environment.
-- Rendered once per environment by scripts/render_sql.py. Retention comes from the environment
-- file because Standard edition caps it at one day.

USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS {{DB}}
    DATA_RETENTION_TIME_IN_DAYS = {{RETENTION}}
    COMMENT = 'SCM Ontology {{ENV}} environment';

CREATE SCHEMA IF NOT EXISTS {{DB}}.RAW
    COMMENT = 'Raw ingested data from source systems';
CREATE SCHEMA IF NOT EXISTS {{DB}}.STAGING
    COMMENT = 'Staging models — cleaned and typed';
CREATE SCHEMA IF NOT EXISTS {{DB}}.CONFORMED
    COMMENT = 'Conformed dimensions and facts'
    DATA_RETENTION_TIME_IN_DAYS = {{LONG_RETENTION}};
CREATE SCHEMA IF NOT EXISTS {{DB}}.SEMANTIC
    COMMENT = 'Semantic views, glossary and governed layer';
CREATE SCHEMA IF NOT EXISTS {{DB}}.AGENT
    COMMENT = 'Cortex Agent and governed procedures';
CREATE SCHEMA IF NOT EXISTS {{DB}}.AUDIT
    COMMENT = 'Answer audit log and evaluation results'
    DATA_RETENTION_TIME_IN_DAYS = {{LONG_RETENTION}};
CREATE SCHEMA IF NOT EXISTS {{DB}}.EVAL
    COMMENT = 'Evaluation truth data and test artefacts';
CREATE SCHEMA IF NOT EXISTS {{DB}}.OPS
    COMMENT = 'Operational metadata — freshness, dbt runs, alerts';

-- Grants
USE ROLE SECURITYADMIN;

GRANT USAGE ON DATABASE {{DB}} TO ROLE SCM_DEPLOY;
GRANT USAGE ON DATABASE {{DB}} TO ROLE SCM_READER;
GRANT USAGE ON ALL SCHEMAS IN DATABASE {{DB}} TO ROLE SCM_READER;
-- Personas read the semantic layer only. Semantic views run with owner's rights, so no persona
-- needs SELECT on CONFORMED; without masking (Standard edition) that grant would expose contact
-- and bank columns. Cortex Analyst needs base-table SELECT, so it stays an owner-side tool.
GRANT SELECT ON FUTURE SEMANTIC VIEWS IN SCHEMA {{DB}}.SEMANTIC TO ROLE SCM_READER;
GRANT SELECT ON FUTURE TABLES IN SCHEMA {{DB}}.SEMANTIC TO ROLE SCM_READER;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA {{DB}}.SEMANTIC TO ROLE SCM_READER;
GRANT SELECT ON FUTURE TABLES IN SCHEMA {{DB}}.AUDIT TO ROLE SCM_READER;

-- SCM_DEPLOY gets full DDL on all schemas
GRANT ALL PRIVILEGES ON ALL SCHEMAS IN DATABASE {{DB}} TO ROLE SCM_DEPLOY;
GRANT ALL PRIVILEGES ON FUTURE TABLES IN DATABASE {{DB}} TO ROLE SCM_DEPLOY;
GRANT ALL PRIVILEGES ON FUTURE VIEWS IN DATABASE {{DB}} TO ROLE SCM_DEPLOY;
