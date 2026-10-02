select
    matnr || '-' || cast(valid_from as varchar) as tariff_id,
    matnr as part_id,
    stawn as hts_code,
    duty_rate,
    valid_from as effective_from,
    valid_to as effective_to
from {{ source('erp', 'material_tariffs') }}
