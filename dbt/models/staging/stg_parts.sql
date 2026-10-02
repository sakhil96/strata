-- Standardise part UOM to base units with pack/pallet factors.

select
    part_id,
    part_name,
    part_family,
    category,
    lower(base_uom) as base_uom,
    pack_factor,
    pallet_factor,
    weight_kg
from {{ source('raw', 'PARTS') }}
