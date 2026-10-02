-- Landed cost: material at the FX rate on the PO date, inbound freight shared by
-- received weight, duty at the rate in force on the day the goods left the
-- supplier, then insurance and handling from the registry constants.

with receipts as (
    select po_line_id, min(receipt_date) as receipt_date, sum(received_qty) as received_qty
    from {{ ref('stg_goods_receipts') }}
    group by po_line_id
),

lines as (
    select
        po.*,
        r.receipt_date,
        coalesce(r.received_qty, 0) as received_qty,
        coalesce(r.received_qty, 0) * p.weight_kg as received_weight_kg,
        fx.rate as fx_rate_order,
        sup.country_code <> pl.country_code as is_import
    from {{ ref('stg_purchase_order_lines') }} po
    left join receipts r on r.po_line_id = po.po_line_id
    join {{ ref('stg_parts') }} p on p.part_id = po.part_id
    join {{ ref('stg_suppliers') }} sup on sup.supplier_id = po.supplier_id
    join {{ source('erp', 'plants') }} pl on pl.plant_id = po.plant_id
    join {{ source('erp', 'fx_rates') }} fx
        on fx.from_currency = po.currency and fx.fx_date = po.order_date
),

inbound as (
    select i.po_no, i.depart_date, i.freight_amt * fx.rate as freight_usd
    from {{ source('tms', 'inbound_shipments') }} i
    join {{ source('erp', 'fx_rates') }} fx
        on fx.from_currency = i.freight_ccy and fx.fx_date = i.depart_date
),

costed as (
    select
        l.*,
        i.depart_date as inbound_ship_date,
        l.unit_cost * l.received_qty * l.fx_rate_order as material_usd,
        coalesce(i.freight_usd * l.received_weight_kg
            / nullif(sum(l.received_weight_kg) over (partition by l.po_number), 0), 0) as freight_usd,
        t.duty_rate
    from lines l
    left join inbound i on i.po_no = l.po_number
    left join {{ ref('dim_tariff_code') }} t
        on t.part_id = l.part_id and i.depart_date between t.effective_from and t.effective_to
)

select
    po_line_id, po_number, line_number, supplier_id, part_id, plant_id, ordered_qty, source_uom,
    unit_cost, currency, order_date, promised_date, confirmed_date, is_cancelled, receipt_date,
    received_qty, inbound_ship_date, is_import, duty_rate, material_usd, freight_usd,
    case when is_import then coalesce(duty_rate, 0) * material_usd else 0 end as duty_usd,
    {{ var('insurance_rate') }} * material_usd as insurance_usd,
    {{ var('handling_usd_per_unit') }} * received_qty as handling_usd,
    material_usd + freight_usd
        + case when is_import then coalesce(duty_rate, 0) * material_usd else 0 end
        + {{ var('insurance_rate') }} * material_usd
        + {{ var('handling_usd_per_unit') }} * received_qty as landed_usd,
    case when received_qty > 0 then 1 else 0 end as is_received,
    case when received_qty > 0 and receipt_date <= promised_date then 1 else 0 end as is_on_time_receipt,
    case when received_qty > 0 then {{ days_between('order_date', 'receipt_date') }} end as lead_days,
    case when received_qty > 0 then {{ month_of('receipt_date') }} end as receipt_month
from costed
