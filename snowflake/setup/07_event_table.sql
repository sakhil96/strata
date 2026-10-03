-- Telemetry for procedures, the agent and the service.

USE ROLE ACCOUNTADMIN;

-- @enterprise
CREATE EVENT TABLE IF NOT EXISTS {{DB}}.OPS.SCM_EVENTS
    COMMENT = 'OpenTelemetry event table for procedures, API and service telemetry';
ALTER DATABASE {{DB}} SET EVENT_TABLE = {{DB}}.OPS.SCM_EVENTS;
-- @end
-- Standard edition cannot associate an event table with a database, so telemetry lands in the
-- account default and OPS.SCM_EVENTS_DEFAULT reads this database's share of it.
CREATE OR REPLACE VIEW {{DB}}.OPS.SCM_EVENTS_DEFAULT AS
    SELECT * FROM SNOWFLAKE.TELEMETRY.EVENTS
    WHERE resource_attributes:"snow.database.name"::STRING = '{{DB}}';

ALTER DATABASE {{DB}} SET LOG_LEVEL = INFO;
ALTER DATABASE {{DB}} SET TRACE_LEVEL = ON_EVENT;

GRANT SELECT ON VIEW {{DB}}.OPS.SCM_EVENTS_DEFAULT TO ROLE SCM_DEPLOY;
