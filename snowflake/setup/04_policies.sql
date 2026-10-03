-- Tags for one environment. {{DB}} is SCM_DEV, SCM_TEST or SCM_PROD.
-- The compiler tags columns from ontology/entitlements.yaml (policies/tags.sql).

USE ROLE SCM_ADMIN;

CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.SENSITIVITY
    ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
    COMMENT = 'Sensitivity from the ontology; drives masking';
CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_OWNER COMMENT = 'Metric owner from the registry';
CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_STEWARD COMMENT = 'Metric steward from the registry';
CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_VERSION COMMENT = 'Metric version from the registry';
-- SCM_DEPLOY creates the semantic views, which carry the registry tags, and rebuilds the tables
-- whose sensitivity tags policies/tags.sql reapplies after every dbt build.
GRANT APPLY ON TAG {{DB}}.CONFORMED.METRIC_OWNER TO ROLE SCM_DEPLOY;
GRANT APPLY ON TAG {{DB}}.CONFORMED.METRIC_STEWARD TO ROLE SCM_DEPLOY;
GRANT APPLY ON TAG {{DB}}.CONFORMED.METRIC_VERSION TO ROLE SCM_DEPLOY;
GRANT APPLY ON TAG {{DB}}.CONFORMED.SENSITIVITY TO ROLE SCM_DEPLOY;

-- Row scope and column rules live in ontology/entitlements.yaml and compile to
-- snowflake/policies/: secure views over CONFORMED on Standard edition, row access and masking
-- policies on Enterprise. The tables they read are GOV.ENTITLEMENTS and GOV.COLUMN_VISIBILITY.
