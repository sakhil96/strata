-- Three key schemes reach us: SUP0001 from the ERP master, V-000001 from the
-- portal, and SUP0001 / V-000001 / VENDOR_1 mixed on purchase orders.
-- Every one carries the same sequence number, so the golden key is the number.
-- A key used by several systems must still map once, or joins fan out.

with keys as (
    select supplier_key as source_key, 'erp' as source_system from {{ source('erp', 'supplier_master') }}
    union all
    select vendor_ref, 'portal' from {{ source('portal', 'supplier_profiles') }}
    union all
    select lifnr, 'erp_po' from {{ source('erp', 'purchase_order_lines') }}
)

select
    source_key,
    min(source_system) as first_seen_in,
    {{ golden_supplier_key('source_key') }} as supplier_id
from keys
group by source_key
