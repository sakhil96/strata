select plant_id, plant_name, plant_type, region, country_code, timezone
from {{ source('erp', 'plants') }}
