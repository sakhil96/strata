select
    lane_id,
    origin_region,
    destination_region,
    mode,
    transit_days_typical
from {{ source('raw', 'LANES') }}
