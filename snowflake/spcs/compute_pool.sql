-- Create the compute pool for STRATA.
-- Smallest available; auto-suspend when idle.

USE ROLE SYSADMIN;

CREATE COMPUTE POOL IF NOT EXISTS SCM_POOL_{{ENV}}
    FOR SERVICE
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_SUSPEND_SECS = 300
    AUTO_RESUME = TRUE
    COMMENT = 'STRATA service compute pool for {{ENV}}';

GRANT USAGE ON COMPUTE POOL SCM_POOL_{{ENV}} TO ROLE SCM_DEPLOY;
