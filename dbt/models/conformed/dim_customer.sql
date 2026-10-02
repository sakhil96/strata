select
    customer_id,
    customer_name,
    ship_to_id,
    sold_to_id,
    account_id,
    segment,
    country_code,
    contact_name,
    contact_email
from {{ source('raw', 'CUSTOMERS') }}
