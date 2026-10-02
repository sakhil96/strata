{# The same models run on Snowflake and DuckDB; these are the only dialect seams. #}

{% macro days_between(start, finish) %}{{ return(adapter.dispatch('days_between')(start, finish)) }}{% endmacro %}
{% macro default__days_between(start, finish) %}datediff('day', {{ start }}, {{ finish }}){% endmacro %}
{% macro snowflake__days_between(start, finish) %}datediff(day, {{ start }}, {{ finish }}){% endmacro %}

{% macro minutes_between(start, finish) %}{{ return(adapter.dispatch('minutes_between')(start, finish)) }}{% endmacro %}
{% macro default__minutes_between(start, finish) %}datediff('minute', {{ start }}, {{ finish }}){% endmacro %}
{% macro snowflake__minutes_between(start, finish) %}datediff(minute, {{ start }}, {{ finish }}){% endmacro %}

{% macro local_to_utc(ts, tz) %}{{ return(adapter.dispatch('local_to_utc')(ts, tz)) }}{% endmacro %}
{% macro default__local_to_utc(ts, tz) %}cast(timezone('UTC', timezone({{ tz }}, {{ ts }})) as timestamp){% endmacro %}
{% macro snowflake__local_to_utc(ts, tz) %}convert_timezone({{ tz }}, 'UTC', {{ ts }}){% endmacro %}

{% macro month_of(d) %}cast(date_trunc('month', {{ d }}) as date){% endmacro %}

{% macro golden_supplier_key(raw_key) %}
'SUP-' || lpad(cast(cast(regexp_replace({{ raw_key }}, '^[^0-9]+', '') as integer) as varchar), 4, '0')
{% endmacro %}

{% macro generate_schema_name(custom_schema_name, node) %}
{{ (custom_schema_name or target.schema) | trim | upper }}
{% endmacro %}
