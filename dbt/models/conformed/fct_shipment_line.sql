select
    shipment_line_id,
    shipment_id,
    so_line_id,
    shipped_qty,
    is_first_shipment
from {{ source('raw', 'SHIPMENT_LINES') }}
