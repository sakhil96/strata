-- Quantities arrive in eaches, cases or pallets; we hold everything in eaches.

select
    po.ebeln || '-' || lpad(cast(po.ebelp as varchar), 5, '0') as po_line_id,
    po.ebeln as po_number,
    po.ebelp as line_number,
    cw.supplier_id,
    po.matnr as part_id,
    po.werks as plant_id,
    po.menge * case po.meins
        when 'EA' then 1
        when 'CS' then p.pack_factor
        when 'PAL' then p.pack_factor * p.cases_per_pallet
    end as ordered_qty,
    po.meins as source_uom,
    po.netpr_per_ea as unit_cost,
    po.waers as currency,
    po.bedat as order_date,
    po.vendor_promise_dt as promised_date,
    po.confirmed_dt as confirmed_date,
    po.loekz = 'L' as is_cancelled
from {{ source('erp', 'purchase_order_lines') }} po
join {{ ref('stg_supplier_crosswalk') }} cw on cw.source_key = po.lifnr
join {{ ref('stg_parts') }} p on p.part_id = po.matnr
