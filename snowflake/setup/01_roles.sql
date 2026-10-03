-- Functional role hierarchy for the SCM Ontology project.
-- SCM_ADMIN > SCM_DEPLOY > persona roles > SCM_READER.

USE ROLE SECURITYADMIN;

CREATE ROLE IF NOT EXISTS SCM_ADMIN
    COMMENT = 'Full administrative access to the SCM Ontology project';
CREATE ROLE IF NOT EXISTS SCM_DEPLOY
    COMMENT = 'Deployment role for CI/CD pipelines';
CREATE ROLE IF NOT EXISTS PLANNING_ROLE
    COMMENT = 'Supply chain planning persona';
CREATE ROLE IF NOT EXISTS PROCUREMENT_ROLE
    COMMENT = 'Procurement and sourcing persona';
CREATE ROLE IF NOT EXISTS LOGISTICS_ROLE
    COMMENT = 'Logistics and transportation persona';
CREATE ROLE IF NOT EXISTS EXECUTIVE_ROLE
    COMMENT = 'Executive and finance persona';
CREATE ROLE IF NOT EXISTS SCM_READER
    COMMENT = 'Read-only base role for all SCM users';

-- Hierarchy
GRANT ROLE SCM_DEPLOY TO ROLE SCM_ADMIN;
GRANT ROLE PLANNING_ROLE TO ROLE SCM_DEPLOY;
GRANT ROLE PROCUREMENT_ROLE TO ROLE SCM_DEPLOY;
GRANT ROLE LOGISTICS_ROLE TO ROLE SCM_DEPLOY;
GRANT ROLE EXECUTIVE_ROLE TO ROLE SCM_DEPLOY;
GRANT ROLE SCM_READER TO ROLE PLANNING_ROLE;
GRANT ROLE SCM_READER TO ROLE PROCUREMENT_ROLE;
GRANT ROLE SCM_READER TO ROLE LOGISTICS_ROLE;
GRANT ROLE SCM_READER TO ROLE EXECUTIVE_ROLE;

-- Grant SCM_ADMIN to SYSADMIN so it is reachable from the standard hierarchy
GRANT ROLE SCM_ADMIN TO ROLE SYSADMIN;

-- Service user for the SPCS container (key-pair auth, no password)
-- Key-pair only: TYPE = SERVICE users cannot hold a password. The public key is set by
-- runbooks/rotate-keys.md, never in this file.
-- The service user's own role carries its entitlement; SCM_READER, which every persona inherits,
-- carries none (ontology/entitlements.yaml).
CREATE ROLE IF NOT EXISTS SCM_SERVICE_ROLE COMMENT = 'The Strata service and its agent calls';
GRANT ROLE SCM_READER TO ROLE SCM_SERVICE_ROLE;
GRANT ROLE SCM_SERVICE_ROLE TO ROLE SCM_DEPLOY;
CREATE USER IF NOT EXISTS SCM_SERVICE_USER
    TYPE = SERVICE
    DEFAULT_ROLE = SCM_SERVICE_ROLE
    DEFAULT_SECONDARY_ROLES = ()
    COMMENT = 'Service account for the Strata container and CI';
GRANT ROLE SCM_SERVICE_ROLE TO USER SCM_SERVICE_USER;

-- The API answers as the caller's persona with USE ROLE, so the service must be able to assume
-- the four personas. They sit on their own role granted to the user, not under SCM_SERVICE_ROLE:
-- a role inherits what it is granted, and SCM_SERVICE_ROLE is what agent:run runs as, so holding
-- them there would put PROCUREMENT_ROLE's columns in every agent session. No secondary roles by
-- default, for the same reason. The mapping from caller to persona is in docs/governance.md.
CREATE ROLE IF NOT EXISTS SCM_SERVICE_PERSONAS COMMENT = 'Personas the Strata service may assume, one at a time';
GRANT ROLE PLANNING_ROLE TO ROLE SCM_SERVICE_PERSONAS;
GRANT ROLE PROCUREMENT_ROLE TO ROLE SCM_SERVICE_PERSONAS;
GRANT ROLE LOGISTICS_ROLE TO ROLE SCM_SERVICE_PERSONAS;
GRANT ROLE EXECUTIVE_ROLE TO ROLE SCM_SERVICE_PERSONAS;
GRANT ROLE SCM_SERVICE_PERSONAS TO USER SCM_SERVICE_USER;
ALTER USER SCM_SERVICE_USER SET DEFAULT_SECONDARY_ROLES = ();

-- A regional planner, scoped to EMEA plants in entitlements.yaml.
CREATE ROLE IF NOT EXISTS EMEA_PLANNING_ROLE COMMENT = 'Planning persona scoped to EMEA plants';
GRANT ROLE SCM_READER TO ROLE EMEA_PLANNING_ROLE;
GRANT ROLE EMEA_PLANNING_ROLE TO ROLE SCM_DEPLOY;

-- Deploy identity for loads, dbt and releases from CI and the deploying workstation. Key-pair
-- only; its public key is set by runbooks/rotate-keys.md.
CREATE USER IF NOT EXISTS SCM_CI_USER
    TYPE = SERVICE
    DEFAULT_ROLE = SCM_DEPLOY
    COMMENT = 'Key-pair identity for loads, dbt and deploys';
GRANT ROLE SCM_DEPLOY TO USER SCM_CI_USER;

-- Reviewers get one read-only role: every persona view, the audit trail and the evaluation
-- results, no masked columns unmasked, no warehouse larger than XSMALL, nothing writable.
CREATE ROLE IF NOT EXISTS JUDGE_ROLE
    COMMENT = 'Read-only reviewer access to the governed views, audit and evaluation';
GRANT ROLE SCM_READER TO ROLE JUDGE_ROLE;
GRANT ROLE JUDGE_ROLE TO ROLE SCM_DEPLOY;
