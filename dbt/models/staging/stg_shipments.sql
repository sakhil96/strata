select
    shipment_id,
    carrier_id,
    lane_id,
    origin_plant_id,
    destination_id,
    to_date(ship_date) as ship_date,
    to_date(carrier_eta) as carrier_eta,
    to_date(actual_delivery) as actual_delivery,
    chargeable_weight_kg,
    freight_charge,
    freight_currency,
    status
from {{ source('raw', 'SHIPMENTS') }}
