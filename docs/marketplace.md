# Optional Marketplace join

Not built. The GSCPI series is fetched locally by `data/reference/fetch_gscpi.py` and not committed,
because its redistribution terms are unconfirmed; no dbt model reads it today.

The intended path on an account: mount a Marketplace listing that carries the same monthly series,
declare it as a dbt source, and join it to the conformed facts on `period_month` as an annotation
for the before/after page. No governed metric would depend on it, so the registry and the semantic
views would not change. Needs an account and a chosen listing.
