select
    receipt_id,
    po_line_id,
    to_date(receipt_date) as receipt_date,
    received_qty,
    quality_status,
    inspector_name
from {{ source('raw', 'GOODS_RECEIPTS') }}
