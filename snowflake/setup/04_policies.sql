-- Row access policies and masking policies.
-- These are created per environment and attached to conformed tables.

USE ROLE SCM_ADMIN;
USE DATABASE {{DB}};

-- Tag for sensitivity classification (from ontology annotations)
CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.SENSITIVITY
    ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
    COMMENT = 'Data sensitivity level from the ontology';

CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_OWNER
    COMMENT = 'Metric owner from the registry';

CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_STEWARD
    COMMENT = 'Metric steward from the registry';

CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_VERSION
    COMMENT = 'Metric version from the registry';

-- Masking policy for CONFIDENTIAL string columns (contact names, emails)
CREATE OR REPLACE MASKING POLICY {{DB}}.CONFORMED.MASK_CONFIDENTIAL_STRING AS
    (val STRING) RETURNS STRING ->
    CASE
        WHEN IS_ROLE_IN_SESSION('SCM_ADMIN') THEN val
        WHEN IS_ROLE_IN_SESSION('EXECUTIVE_ROLE') THEN val
        ELSE '***MASKED***'
    END;

-- Masking policy for RESTRICTED numeric columns (bank details, unit costs for non-procurement)
CREATE OR REPLACE MASKING POLICY {{DB}}.CONFORMED.MASK_RESTRICTED_NUMBER AS
    (val NUMBER(38,6)) RETURNS NUMBER(38,6) ->
    CASE
        WHEN IS_ROLE_IN_SESSION('SCM_ADMIN') THEN val
        WHEN IS_ROLE_IN_SESSION('PROCUREMENT_ROLE') THEN val
        WHEN IS_ROLE_IN_SESSION('EXECUTIVE_ROLE') THEN val
        ELSE NULL
    END;

-- Row access policy: users see only their region unless admin or executive
CREATE OR REPLACE ROW ACCESS POLICY {{DB}}.CONFORMED.REGION_ACCESS AS
    (region_code STRING) RETURNS BOOLEAN ->
    IS_ROLE_IN_SESSION('SCM_ADMIN')
    OR IS_ROLE_IN_SESSION('EXECUTIVE_ROLE')
    OR IS_ROLE_IN_SESSION('SCM_DEPLOY')
    OR (IS_ROLE_IN_SESSION('PLANNING_ROLE') AND region_code IN ('US', 'EMEA', 'APAC'))
    OR (IS_ROLE_IN_SESSION('PROCUREMENT_ROLE') AND region_code IN ('US', 'EMEA', 'APAC'))
    OR (IS_ROLE_IN_SESSION('LOGISTICS_ROLE') AND region_code IN ('US', 'EMEA', 'APAC'));
    -- In production, replace with a mapping table join per user/role to region.
