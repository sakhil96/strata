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
    to_date(requested_date) as requested_date,
    to_date(committed_date) as committed_date,
    to_date(actual_ship_date) as actual_ship_date,
    to_date(actual_delivery_date) as actual_delivery_date,
    to_date(order_date) as order_date,
    status
from {{ source('raw', 'SALES_ORDER_LINES') }}
