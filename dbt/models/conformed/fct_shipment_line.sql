-- Freight is shared across a shipment's lines by chargeable weight.

with weighed as (
    select
        sl.*,
        l.part_id,
        sl.shipped_qty * p.weight_kg as line_weight_kg
    from {{ ref('stg_shipment_lines') }} sl
    join {{ ref('stg_sales_order_lines') }} l on l.so_line_id = sl.so_line_id
    join {{ ref('stg_parts') }} p on p.part_id = l.part_id
)

select
    w.shipment_line_id, w.shipment_id, w.so_line_id, w.part_id, w.shipped_qty, w.is_first_shipment,
    w.line_weight_kg, s.plant_id, s.customer_id, s.carrier_id, s.ship_date,
    s.freight_usd * w.line_weight_kg / sum(w.line_weight_kg) over (partition by w.shipment_id)
        as freight_alloc_usd,
    {{ month_of('s.ship_date') }} as ship_month
from weighed w
join {{ ref('stg_shipments') }} s on s.shipment_id = w.shipment_id
