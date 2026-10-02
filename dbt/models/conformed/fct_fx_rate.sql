select fx_date, from_currency, to_currency, rate
from {{ source('erp', 'fx_rates') }}
