select
    matnr as part_id,
    maktx as part_name,
    prodh_family as part_family,
    prodh_category as category,
    meins as base_uom,
    ea_per_cs as pack_factor,
    cs_per_pal as cases_per_pallet,
    ntgew_kg as weight_kg,
    stprs_usd as std_cost_usd,
    stawn as hts_code
from {{ source('erp', 'material_master') }}
