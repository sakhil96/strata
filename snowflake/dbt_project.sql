-- dbt Projects on Snowflake: the same dbt/ directory, deployed from the repository object.
USE ROLE SCM_DEPLOY;

CREATE OR REPLACE DBT PROJECT {{DB}}.OPS.SCM_DBT
    FROM '@{{DB}}.OPS.SCM_REPO/branches/main/dbt'
    DEFAULT_TARGET = '{{ENV}}'
    COMMENT = 'Staging and conformed models for the supply chain ontology';
