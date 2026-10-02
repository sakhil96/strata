select carrier_id, carrier_name, carrier_type, scac_code, home_region
from {{ source('tms', 'carriers') }}
