-- Conformed PO lines joined with supplier crosswalk for golden keys.

select
    pol.po_line_id,
    pol.po_number,
    pol.line_number,
    s.supplier_id,
    pol.part_id,
    pol.deliver_to_plant_id,
    pol.ordered_qty,
    pol.unit_cost,
    pol.currency,
    pol.order_date,
    pol.promised_date,
    pol.confirmed_date,
    pol.status
from {{ ref('stg_purchase_order_lines') }} pol
inner join {{ ref('stg_suppliers') }} s on pol.supplier_id = s.supplier_id
