-- The portal repeats some suppliers in upper case with trailing dots; the ERP
-- master is the system of record for names, the portal only for contacts.

select
    cw.supplier_id,
    m.name1 as supplier_name,
    m.site as supplier_site,
    {{ golden_supplier_key('m.parent_key') }} as parent_supplier_id,
    m.land1 as country_code,
    m.waers as currency,
    m.contact as contact_name,
    m.email as contact_email,
    m.iban as bank_account
from {{ source('erp', 'supplier_master') }} m
join {{ ref('stg_supplier_crosswalk') }} cw
    on cw.source_key = m.supplier_key
