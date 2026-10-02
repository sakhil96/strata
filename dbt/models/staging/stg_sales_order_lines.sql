select
    s.vbeln || '-' || lpad(cast(s.posnr as varchar), 3, '0') as so_line_id,
    s.vbeln as so_number,
    s.posnr as line_number,
    s.kunwe as customer_id,
    s.matnr as part_id,
    s.lgort as storage_location_id,
    l.plant_id,
    s.kwmeng_ea as ordered_qty,
    s.audat as order_date,
    s.req_dlv_date as requested_date,
    s.conf_dlv_date as committed_date,
    s.abgru <> '' as is_cancelled
from {{ source('erp', 'sales_order_lines') }} s
join {{ source('erp', 'storage_locations') }} l on l.storage_location_id = s.lgort
