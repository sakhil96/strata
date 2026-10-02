-- On Snowflake this model is replaced by a dynamic table with a five-minute lag
-- (snowflake/dynamic_tables/fct_delivery_event.sql); locally it is a table.
select * from {{ ref('stg_delivery_events') }}
