-- Some sites report local wall-clock time; TS_BASIS says which. Proof of delivery
-- is sometimes re-sent days later, so only the first POD per shipment counts.

with normalised as (
    select
        event_id,
        shipment_no as shipment_id,
        case event_code
            when 'PU' then 'picked_up'
            when 'DEP' then 'departed'
            when 'ARR' then 'arrived'
            when 'POD' then 'delivered'
            when 'EXC' then 'exception'
        end as event_type,
        case ts_basis
            when 'LOCAL' then {{ local_to_utc('event_ts', 'site_tz') }}
            else event_ts
        end as event_time_utc,
        site_tz,
        received_at
    from {{ source('portal', 'delivery_events') }}
),

ranked as (
    select
        *,
        row_number() over (partition by shipment_id, event_type order by event_time_utc, event_id) as nth
    from normalised
)

select event_id, shipment_id, event_type, event_time_utc, site_tz, received_at
from ranked
where event_type <> 'delivered' or nth = 1
