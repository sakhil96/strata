select
    shipment_id,
    carrier_id,
    lane_id,
    origin_plant_id,
    destination_id,
    ship_date,
    carrier_eta,
    actual_delivery,
    chargeable_weight_kg,
    freight_charge,
    freight_currency,
    status
from {{ ref('stg_shipments') }}
