with milestones as (
    select
        shipment_id,
        min(case when event_type = 'picked_up' then event_time_utc end) as picked_up_utc,
        min(case when event_type = 'delivered' then event_time_utc end) as delivered_utc
    from {{ ref('stg_delivery_events') }}
    group by shipment_id
)

select
    s.shipment_id, s.carrier_id, s.plant_id, s.customer_id, s.ship_date, s.carrier_eta,
    s.actual_delivery, s.chargeable_weight_kg, s.freight_charge, s.freight_currency, s.freight_usd,
    m.picked_up_utc, m.delivered_utc,
    case when s.actual_delivery is not null then 1 else 0 end as is_delivered,
    case when s.actual_delivery <= s.carrier_eta then 1 else 0 end as is_on_eta,
    case when s.actual_delivery is not null
        then {{ minutes_between('m.picked_up_utc', 'm.delivered_utc') }} / 60.0 end as transit_hours_elapsed,
    {{ month_of('s.actual_delivery') }} as delivery_month
from {{ ref('stg_shipments') }} s
left join milestones m on m.shipment_id = s.shipment_id
