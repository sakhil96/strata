-- Exception notes get a cause and a customer-impact flag; clauses and procedures keep the
-- category their source system gave them.

select
    doc_id,
    kind,
    related_id,
    title,
    body,
    source_system,
    case when kind = 'exception_note' then {{ note_category('body', 'category') }} else category end as category,
    case when kind = 'exception_note' then {{ note_is_customer_impacting('body', 'is_customer_impacting') }} else false end
        as is_customer_impacting,
    category as source_category
from {{ source('content', 'documents') }}
