select
    carrier_id,
    carrier_name,
    carrier_type,
    scac_code
from {{ source('raw', 'CARRIERS') }}
