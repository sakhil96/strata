select customer_id, customer_name, sold_to_id, account_id, account_name, segment,
       country_code, region as customer_region, contact_name, contact_email
from {{ source('erp', 'customer_master') }}
