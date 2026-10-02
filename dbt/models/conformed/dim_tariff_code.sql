select
    tariff_id,
    hts_code,
    description,
    duty_rate,
    to_date(effective_from) as effective_from,
    to_date(effective_to) as effective_to,
    part_id
from {{ source('raw', 'TARIFF_CODES') }}
