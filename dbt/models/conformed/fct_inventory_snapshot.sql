select
    snapshot_id,
    storage_location_id,
    part_id,
    to_date(snapshot_date) as snapshot_date,
    on_hand_qty,
    on_hand_value_std,
    in_transit_qty,
    allocated_qty
from {{ source('raw', 'INVENTORY_SNAPSHOTS') }}
