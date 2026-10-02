-- Distribution centres count some parts in cases.

select
    i.lgort as storage_location_id,
    l.plant_id,
    i.matnr as part_id,
    i.snap_date as snapshot_date,
    i.on_hand * case i.uom when 'CS' then p.pack_factor else 1 end as on_hand_qty,
    i.allocated_ea as allocated_qty,
    p.std_cost_usd
from {{ source('iot', 'inventory_snapshots') }} i
join {{ source('erp', 'storage_locations') }} l on l.storage_location_id = i.lgort
join {{ ref('stg_parts') }} p on p.part_id = i.matnr
