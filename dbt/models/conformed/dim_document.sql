select doc_id, kind, related_id, title, body, source_system, category, is_customer_impacting, source_category
from {{ ref('stg_documents') }}
