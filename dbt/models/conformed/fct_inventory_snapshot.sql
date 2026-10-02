with shipped as (
    select l.storage_location_id, sl.part_id, sl.ship_date as shipped_on, sum(sl.shipped_qty) as shipped_qty
    from {{ ref('fct_shipment_line') }} sl
    join {{ ref('stg_sales_order_lines') }} l on l.so_line_id = sl.so_line_id
    group by 1, 2, 3
)

select
    i.storage_location_id, i.plant_id, i.part_id, i.snapshot_date, i.on_hand_qty, i.allocated_qty,
    i.on_hand_qty * i.std_cost_usd as on_hand_value_std,
    coalesce(s.shipped_qty, 0) as shipped_qty,
    coalesce(s.shipped_qty, 0) * i.std_cost_usd as cogs_usd,
    case when i.on_hand_qty = 0 and i.allocated_qty > 0 then 1 else 0 end as is_stockout
from {{ ref('stg_inventory_snapshots') }} i
left join shipped s
    on s.storage_location_id = i.storage_location_id and s.part_id = i.part_id
    and s.shipped_on = i.snapshot_date
