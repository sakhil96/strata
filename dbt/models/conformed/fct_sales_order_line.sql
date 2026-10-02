select
    so_line_id,
    so_number,
    line_number,
    customer_id,
    part_id,
    fulfilled_from_location_id,
    ordered_qty,
    unit_price,
    currency,
    requested_date,
    committed_date,
    actual_ship_date,
    actual_delivery_date,
    order_date,
    status
from {{ ref('stg_sales_order_lines') }}
