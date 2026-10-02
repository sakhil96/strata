select
    receipt_id,
    po_line_id,
    receipt_date,
    received_qty,
    quality_status,
    inspector_name
from {{ ref('stg_goods_receipts') }}
