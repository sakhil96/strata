-- On Snowflake this relation is the dynamic table in snowflake/dynamic_tables/fct_delivery_event.sql,
-- five minutes behind RAW; the snowflake targets disable this model so dbt never replaces it.
{{ config(enabled=target.type != 'snowflake') }}

select * from {{ ref('stg_delivery_events') }}
