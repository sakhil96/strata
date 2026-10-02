-- Secret objects for the SPCS service.
-- Actual key values are set through Snowflake CLI or Snowsight, never in this file.

USE ROLE SCM_ADMIN;
USE DATABASE {{DB}};

-- Service account key pair (public key set separately via ALTER USER)
CREATE SECRET IF NOT EXISTS {{DB}}.AGENT.SCM_SERVICE_KEY
    TYPE = GENERIC_STRING
    SECRET_STRING = 'set-via-cli'
    COMMENT = 'RSA private key for SCM_SERVICE_USER — rotate quarterly per runbooks/rotate-keys.md';

-- Notification integration webhook (if using webhook instead of email)
CREATE SECRET IF NOT EXISTS {{DB}}.OPS.WEBHOOK_SECRET
    TYPE = GENERIC_STRING
    SECRET_STRING = 'set-via-cli'
    COMMENT = 'Webhook URL for alert delivery';
