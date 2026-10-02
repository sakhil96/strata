-- Event table for OpenTelemetry-style observability.

USE ROLE ACCOUNTADMIN;

CREATE EVENT TABLE IF NOT EXISTS {{DB}}.OPS.SCM_EVENTS
    COMMENT = 'OpenTelemetry event table for procedures, API and service telemetry';

-- Set as the account event table (one per account)
ALTER ACCOUNT SET EVENT_TABLE = '{{DB}}.OPS.SCM_EVENTS';

-- Set log and trace levels for the database
ALTER DATABASE {{DB}} SET LOG_LEVEL = INFO;
ALTER DATABASE {{DB}} SET TRACE_LEVEL = ON_EVENT;

-- Grant access for operational monitoring
USE ROLE SECURITYADMIN;
GRANT SELECT ON TABLE {{DB}}.OPS.SCM_EVENTS TO ROLE SCM_DEPLOY;
GRANT SELECT ON TABLE {{DB}}.OPS.SCM_EVENTS TO ROLE SCM_READER;
