-- Resolve three supplier key schemes to a golden key via crosswalk.
-- Source systems use SUP0001, V-000001 and VENDOR_1 formats.

with raw_suppliers as (
    select * from {{ source('raw', 'SUPPLIERS') }}
),

crosswalk as (
    select
        supplier_id as source_key,
        'SUP-' || lpad(
            regexp_replace(
                regexp_replace(
                    regexp_replace(supplier_id, '^SUP', ''),
                    '^V-0*', ''
                ),
                '^VENDOR_', ''
            ), 4, '0'
        ) as golden_key
    from raw_suppliers
)

select
    cw.golden_key as supplier_id,
    s.supplier_name,
    s.supplier_site,
    case
        when s.parent_supplier_id is not null
        then 'SUP-' || lpad(
            regexp_replace(
                regexp_replace(
                    regexp_replace(s.parent_supplier_id, '^SUP', ''),
                    '^V-0*', ''
                ),
                '^VENDOR_', ''
            ), 4, '0'
        )
    end as parent_supplier_id,
    s.country_code,
    s.contact_name,
    s.contact_email,
    s.bank_account,
    s.currency
from raw_suppliers s
inner join crosswalk cw on s.supplier_id = cw.source_key
