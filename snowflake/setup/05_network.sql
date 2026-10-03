-- Network policy for the service user. Origins: the deploying workstation (STRATA_ORIGIN_CIDR,
-- rendered) and GitHub Actions through Snowflake's managed rule. Applied to the service user here;
-- the account-level policy is applied by hand only after a login test passes from an allowed origin.

USE ROLE ACCOUNTADMIN;

CREATE NETWORK RULE IF NOT EXISTS {{DB}}.OPS.SCM_TEAM_ORIGINS
    MODE = INGRESS
    TYPE = IPV4
    VALUE_LIST = ('{{ORIGIN_CIDR}}')
    COMMENT = 'Deploying workstation';

CREATE NETWORK POLICY IF NOT EXISTS SCM_{{ENV}}_NETWORK_POLICY
    ALLOWED_NETWORK_RULE_LIST = ('{{DB}}.OPS.SCM_TEAM_ORIGINS', 'SNOWFLAKE.NETWORK_SECURITY.GITHUBACTIONS_GLOBAL')
    COMMENT = 'Team and CI origins for STRATA {{ENV}}';

ALTER USER SCM_SERVICE_USER SET NETWORK_POLICY = SCM_{{ENV}}_NETWORK_POLICY;
ALTER USER SCM_CI_USER SET NETWORK_POLICY = SCM_{{ENV}}_NETWORK_POLICY;
