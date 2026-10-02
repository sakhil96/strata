select
    mblnr as receipt_id,
    ebeln || '-' || lpad(cast(ebelp as varchar), 5, '0') as po_line_id,
    budat as receipt_date,
    qty_ea as received_qty,
    quality as quality_status
from {{ source('erp', 'goods_receipts') }}
