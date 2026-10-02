-- Inventory measures do not add across time: month-end position, trailing 90-day
-- shipments at that month end, and month averages for the finance basis.

with daily as (
    select
        *,
        {{ month_of('snapshot_date') }} as snapshot_month,
        sum(cogs_usd) over (partition by storage_location_id, part_id order by snapshot_date
                            rows between 89 preceding and current row) as cogs_90d,
        sum(shipped_qty) over (partition by storage_location_id, part_id order by snapshot_date
                               rows between 89 preceding and current row) as units_90d,
        row_number() over (partition by storage_location_id, part_id, {{ month_of('snapshot_date') }}
                           order by snapshot_date desc) as from_end
    from {{ ref('fct_inventory_snapshot') }}
)

select
    storage_location_id,
    part_id,
    snapshot_month,
    max(plant_id) as plant_id,
    max(case when from_end = 1 then on_hand_value_std end) as on_hand_value_end,
    max(case when from_end = 1 then on_hand_qty end) as on_hand_qty_end,
    max(case when from_end = 1 then cogs_90d end) / 90.0 as cogs_daily_90d,
    max(case when from_end = 1 then units_90d end) / 90.0 as units_daily_90d,
    max(case when from_end = 1 then cogs_90d end) / 90.0 * 365 as cogs_annual_90d,
    sum(is_stockout) as stockout_days,
    count(*) as obs_days,
    avg(on_hand_value_std) * count(*) as avg_value_x_days,
    sum(cogs_usd) as cogs_month
from daily
group by storage_location_id, part_id, snapshot_month
