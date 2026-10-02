select
    storage_location_id,
    storage_location_name,
    plant_id,
    location_type
from {{ source('raw', 'STORAGE_LOCATIONS') }}
