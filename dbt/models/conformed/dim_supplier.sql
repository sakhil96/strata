select
    supplier_id,
    supplier_name,
    supplier_site,
    parent_supplier_id,
    country_code,
    contact_name,
    contact_email,
    bank_account,
    currency
from {{ ref('stg_suppliers') }}
