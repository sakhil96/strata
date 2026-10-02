-- Network policies for the SCM Ontology project.

USE ROLE SECURITYADMIN;

-- Network rule for the team's known origins (replace with actual CIDRs)
CREATE OR REPLACE NETWORK RULE SCM_TEAM_ORIGINS
    MODE = INGRESS
    TYPE = IPV4
    VALUE_LIST = ('0.0.0.0/0')  -- Replace with actual team and CI runner CIDRs
    COMMENT = 'Team and CI runner IP ranges';

-- Network policy applied at account level
CREATE OR REPLACE NETWORK POLICY SCM_NETWORK_POLICY
    ALLOWED_NETWORK_RULE_LIST = ('SCM_TEAM_ORIGINS')
    COMMENT = 'Restrict account access to known origins';

-- Apply to account (uncomment when CIDRs are configured)
-- ALTER ACCOUNT SET NETWORK_POLICY = SCM_NETWORK_POLICY;

-- Apply to the service user
-- ALTER USER SCM_SERVICE_USER SET NETWORK_POLICY = SCM_NETWORK_POLICY;
