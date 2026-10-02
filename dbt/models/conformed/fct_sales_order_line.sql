-- The five dates stay distinct: requested, committed, order, ship and delivery.
-- A line's delivery is the proof of delivery of its first shipment leg.

with first_leg as (
    select sl.so_line_id, sl.shipped_qty, s.ship_date, s.actual_delivery
    from {{ ref('stg_shipment_lines') }} sl
    join {{ ref('stg_shipments') }} s on s.shipment_id = sl.shipment_id
    where sl.is_first_shipment
),

lines as (
    select
        l.*,
        coalesce(f.shipped_qty, 0) as first_shipment_qty,
        f.ship_date as actual_ship_date,
        case when not l.is_cancelled then f.actual_delivery end as actual_delivery_date
    from {{ ref('stg_sales_order_lines') }} l
    left join first_leg f on f.so_line_id = l.so_line_id
),

flagged as (
    select
        *,
        case when actual_delivery_date is not null then 1 else 0 end as is_delivered,
        case when actual_delivery_date <= committed_date then 1 else 0 end as is_on_time,
        case when actual_delivery_date <= requested_date then 1 else 0 end as is_on_time_to_request,
        case when actual_delivery_date <= committed_date and first_shipment_qty >= ordered_qty
            then 1 else 0 end as is_otif,
        case when is_cancelled then 0 else 1 end as is_live,
        case when is_cancelled then 0 else ordered_qty end as live_ordered_qty,
        case when is_cancelled then 0 else first_shipment_qty end as live_first_qty,
        case when not is_cancelled and first_shipment_qty >= ordered_qty then 1 else 0 end as is_line_filled,
        case when actual_delivery_date is not null
            then {{ days_between('order_date', 'actual_delivery_date') }} end as cycle_days
    from lines
),

orders as (
    select
        so_number,
        min(line_number) as head_line,
        min(is_line_filled) as all_filled
    from flagged
    where is_live = 1
    group by so_number
)

select
    f.so_line_id, f.so_number, f.line_number, f.customer_id, f.part_id, f.storage_location_id,
    f.plant_id, f.ordered_qty, f.first_shipment_qty, f.order_date, f.requested_date,
    f.committed_date, f.actual_ship_date, f.actual_delivery_date, f.is_cancelled,
    f.is_delivered, f.is_on_time, f.is_on_time_to_request, f.is_otif, f.is_live,
    f.live_ordered_qty, f.live_first_qty, f.is_line_filled, f.cycle_days,
    case when o.head_line = f.line_number then 1 else 0 end as is_order_head,
    case when o.head_line = f.line_number then o.all_filled else 0 end as is_order_filled,
    {{ month_of('f.actual_delivery_date') }} as delivery_month,
    {{ month_of('f.requested_date') }} as request_month
from flagged f
left join orders o on o.so_number = f.so_number
