select
    to_date(fx_date) as fx_date,
    from_currency,
    to_currency,
    rate
from {{ source('raw', 'FX_RATES') }}
