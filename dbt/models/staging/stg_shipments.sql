-- Carriers bill in their home currency; we convert at the rate on the departure date.

select
    s.shipment_no as shipment_id,
    c.carrier_id,
    s.origin_plant as plant_id,
    s.ship_to as customer_id,
    s.depart_date as ship_date,
    s.carrier_eta,
    s.pod_date as actual_delivery,
    s.chg_weight_kg as chargeable_weight_kg,
    s.freight_amt as freight_charge,
    s.freight_ccy as freight_currency,
    s.freight_amt * fx.rate as freight_usd
from {{ source('tms', 'shipments') }} s
join {{ source('tms', 'carriers') }} c on c.scac_code = s.carrier_scac
join {{ source('erp', 'fx_rates') }} fx
    on fx.from_currency = s.freight_ccy and fx.fx_date = s.depart_date
