-- Tags, masking and row access for one environment. {{DB}} is SCM_DEV, SCM_TEST or SCM_PROD.
-- The compiler tags columns from the ontology's sensitivity annotations (semantic/policies.sql);
-- this file owns the policies those tags carry.

USE ROLE SCM_ADMIN;

CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.SENSITIVITY
    ALLOWED_VALUES 'PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'
    COMMENT = 'Sensitivity from the ontology; drives masking';
CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_OWNER COMMENT = 'Metric owner from the registry';
CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_STEWARD COMMENT = 'Metric steward from the registry';
CREATE TAG IF NOT EXISTS {{DB}}.CONFORMED.METRIC_VERSION COMMENT = 'Metric version from the registry';

-- @enterprise
-- CONFIDENTIAL: contact names and emails, readable by admin and executive.
-- RESTRICTED: bank details and commercial cost, readable by admin and procurement only.
CREATE MASKING POLICY IF NOT EXISTS {{DB}}.CONFORMED.MASK_BY_SENSITIVITY_STRING AS (val STRING) RETURNS STRING ->
    CASE SYSTEM$GET_TAG_ON_CURRENT_COLUMN('{{DB}}.CONFORMED.SENSITIVITY')
        WHEN 'CONFIDENTIAL' THEN
            IFF(IS_ROLE_IN_SESSION('SCM_ADMIN') OR IS_ROLE_IN_SESSION('EXECUTIVE_ROLE'), val, '***')
        WHEN 'RESTRICTED' THEN
            IFF(IS_ROLE_IN_SESSION('SCM_ADMIN') OR IS_ROLE_IN_SESSION('PROCUREMENT_ROLE'), val, '***')
        ELSE val
    END;

CREATE MASKING POLICY IF NOT EXISTS {{DB}}.CONFORMED.MASK_BY_SENSITIVITY_NUMBER AS (val NUMBER(38, 6)) RETURNS NUMBER(38, 6) ->
    CASE SYSTEM$GET_TAG_ON_CURRENT_COLUMN('{{DB}}.CONFORMED.SENSITIVITY')
        WHEN 'RESTRICTED' THEN
            IFF(IS_ROLE_IN_SESSION('SCM_ADMIN') OR IS_ROLE_IN_SESSION('PROCUREMENT_ROLE'), val, NULL)
        ELSE val
    END;

ALTER TAG {{DB}}.CONFORMED.SENSITIVITY SET
    MASKING POLICY {{DB}}.CONFORMED.MASK_BY_SENSITIVITY_STRING,
    MASKING POLICY {{DB}}.CONFORMED.MASK_BY_SENSITIVITY_NUMBER;

-- @end

-- Who may see which plant. Rows are maintained through runbooks/revoke-access.md, never ad hoc.
CREATE TABLE IF NOT EXISTS {{DB}}.CONFORMED.USER_PLANT_SCOPE (
    role_name STRING NOT NULL,
    plant_id STRING NOT NULL,
    granted_by STRING NOT NULL,
    granted_on DATE NOT NULL
);

-- Personas share one plant scope so that the same question returns the same number for
-- every role; the scope table is where a regional restriction would be expressed.
MERGE INTO {{DB}}.CONFORMED.USER_PLANT_SCOPE t
USING (
    SELECT r.role_name, p.plant_id
    FROM (SELECT column1 AS role_name FROM VALUES ('PLANNING_ROLE'), ('PROCUREMENT_ROLE'), ('LOGISTICS_ROLE'), ('JUDGE_ROLE')) r
    CROSS JOIN (SELECT column1 AS plant_id FROM VALUES ('PLT-US01'), ('PLT-DE01'), ('PLT-SG01'), ('DC-US01'), ('DC-NL01')) p
) s
ON t.role_name = s.role_name AND t.plant_id = s.plant_id
WHEN NOT MATCHED THEN INSERT VALUES (s.role_name, s.plant_id, 'baseline', CURRENT_DATE());

-- @enterprise
CREATE ROW ACCESS POLICY IF NOT EXISTS {{DB}}.CONFORMED.PLANT_ACCESS AS (plant STRING) RETURNS BOOLEAN ->
    IS_ROLE_IN_SESSION('SCM_ADMIN')
    OR IS_ROLE_IN_SESSION('EXECUTIVE_ROLE')
    OR EXISTS (
        SELECT 1 FROM {{DB}}.CONFORMED.USER_PLANT_SCOPE s
        WHERE s.plant_id = plant AND IS_ROLE_IN_SESSION(s.role_name)
    );
-- @end
