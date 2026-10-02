-- Delivery events land continuously from the carrier portal, so on Snowflake the conformed
-- event fact is a dynamic table five minutes behind RAW rather than a nightly dbt table.
-- The SQL is the dbt staging logic with the portable macros expanded for Snowflake.

USE ROLE SCM_DEPLOY;

CREATE OR REPLACE DYNAMIC TABLE {{DB}}.CONFORMED.FCT_DELIVERY_EVENT
  TARGET_LAG = '5 minutes'
  WAREHOUSE = {{WH}}
  REFRESH_MODE = INCREMENTAL
  COMMENT = 'Delivery events in UTC, first proof of delivery per shipment'
AS
WITH normalised AS (
    SELECT
        event_id,
        shipment_no AS shipment_id,
        DECODE(event_code, 'PU', 'picked_up', 'DEP', 'departed', 'ARR', 'arrived', 'POD', 'delivered', 'EXC', 'exception')
            AS event_type,
        IFF(ts_basis = 'LOCAL', CONVERT_TIMEZONE(site_tz, 'UTC', event_ts), event_ts) AS event_time_utc,
        site_tz,
        received_at
    FROM {{DB}}.RAW.DELIVERY_EVENTS
)
SELECT event_id, shipment_id, event_type, event_time_utc, site_tz, received_at
FROM normalised
QUALIFY event_type <> 'delivered'
     OR ROW_NUMBER() OVER (PARTITION BY shipment_id, event_type ORDER BY event_time_utc, event_id) = 1;
