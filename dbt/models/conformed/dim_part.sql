select
    part_id,
    part_name,
    part_family,
    category,
    base_uom,
    pack_factor,
    pallet_factor,
    weight_kg
from {{ ref('stg_parts') }}
