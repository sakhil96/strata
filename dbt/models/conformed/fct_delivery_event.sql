select
    event_id,
    shipment_id,
    event_type,
    event_time_utc,
    site_tz,
    location_id
from {{ ref('stg_delivery_events') }}
