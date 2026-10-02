select
    shipment_no || '-' || vbeln || '-' || lpad(cast(posnr as varchar), 3, '0') as shipment_line_id,
    shipment_no as shipment_id,
    vbeln || '-' || lpad(cast(posnr as varchar), 3, '0') as so_line_id,
    shipped_qty_ea as shipped_qty,
    leg = 1 as is_first_shipment
from {{ source('tms', 'shipment_lines') }}
