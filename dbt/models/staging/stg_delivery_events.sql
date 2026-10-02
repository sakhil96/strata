-- Deduplicate late-arriving delivery events: keep the earliest event per shipment + type.

with ranked as (
    select
        event_id,
        shipment_id,
        event_type,
        to_timestamp_ntz(event_time_utc) as event_time_utc,
        site_tz,
        location_id,
        row_number() over (
            partition by shipment_id, event_type
            order by to_timestamp_ntz(event_time_utc)
        ) as rn
    from {{ source('raw', 'DELIVERY_EVENTS') }}
)

select
    event_id,
    shipment_id,
    event_type,
    event_time_utc,
    site_tz,
    location_id
from ranked
where rn = 1
