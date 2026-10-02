-- Resolve PO date field inconsistencies and standardise UOM to base units.
-- Source has five different date field names; we take promised_date as canonical.

select
    po_line_id,
    po_number,
    line_number,
    supplier_id,
    part_id,
    deliver_to_plant_id,
    ordered_qty,
    unit_cost,
    currency,
    to_date(order_date) as order_date,
    to_date(promised_date) as promised_date,
    to_date(confirmed_date) as confirmed_date,
    status,
    case lower(uom)
        when 'ea' then 'each'
        when 'each' then 'each'
        when 'cs' then 'case'
        when 'case' then 'case'
        else lower(uom)
    end as uom
from {{ source('raw', 'PURCHASE_ORDER_LINES') }}
