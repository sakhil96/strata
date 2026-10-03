# Governed metrics

Compiled from ontology/metrics.yaml by ontology/compile.py; the expression is the one every
semantic view carries, and suite 1 checks it against truth.

## On-time delivery (`on_time_delivery`)

Share of delivered sales order lines that arrived on or before the date we committed to the customer.

- Formula: SUM(is_on_time) / SUM(is_delivered), lines dated by actual_delivery_date, cancelled lines excluded from both.
- Numerator: Delivered, non-cancelled lines with actual_delivery_date <= committed_date.
- Denominator: Delivered, non-cancelled lines with actual_delivery_date in the period.
- Grain sales_order_line; dated by actual_delivery_date; window period; unit ratio
- Expression: `SUM(delivered_lines.is_on_time) / NULLIF(SUM(delivered_lines.is_delivered), 0)`
- Owner VP Supply Chain; steward Supply Chain Analytics Lead; version 1, approved

## On-time to request (`on_time_to_request`), variant of `on_time_delivery`

Share of delivered sales order lines that arrived on or before the date the customer asked for.

- Formula: SUM(is_on_time_to_request) / SUM(is_delivered), dated by actual_delivery_date.
- Numerator: Delivered, non-cancelled lines with actual_delivery_date <= requested_date.
- Denominator: Delivered, non-cancelled lines with actual_delivery_date in the period.
- Grain sales_order_line; dated by actual_delivery_date; window period; unit ratio
- Expression: `SUM(delivered_lines.is_on_time_to_request) / NULLIF(SUM(delivered_lines.is_delivered), 0)`
- Owner VP Supply Chain; steward Supply Chain Analytics Lead; version 1, approved

## Supplier on-time receipt (`supplier_on_time_receipt`), variant of `on_time_delivery`

Share of received purchase order lines that arrived on or before the supplier's promised date.

- Formula: SUM(is_on_time_receipt) / SUM(is_received), dated by receipt_date.
- Numerator: Received PO lines with receipt_date <= promised_date.
- Denominator: Received PO lines with receipt_date in the period.
- Grain purchase_order_line; dated by receipt_date; window period; unit ratio
- Expression: `SUM(po_lines.is_on_time_receipt) / NULLIF(SUM(po_lines.is_received), 0)`
- Owner VP Procurement; steward Procurement Analytics Lead; version 1, approved

## Carrier on-time (`carrier_on_time`), variant of `on_time_delivery`

Share of delivered shipments that arrived on or before the carrier's own estimate.

- Formula: SUM(is_on_eta) / SUM(is_delivered), shipments dated by actual_delivery.
- Numerator: Delivered shipments with actual_delivery <= carrier_eta.
- Denominator: Delivered shipments with actual_delivery in the period.
- Grain shipment; dated by actual_delivery; window period; unit ratio
- Expression: `SUM(shipments.is_on_eta) / NULLIF(SUM(shipments.is_delivered), 0)`
- Owner VP Logistics; steward Logistics Analytics Lead; version 1, approved

## On-time in-full (`otif`)

Share of delivered sales order lines that were on time to commit and complete on the first shipment.

- Formula: SUM(is_otif) / SUM(is_delivered), dated by actual_delivery_date.
- Numerator: Delivered lines on time to commit whose first shipment covered the ordered quantity.
- Denominator: Delivered, non-cancelled lines with actual_delivery_date in the period.
- Grain sales_order_line; dated by actual_delivery_date; window period; unit ratio
- Expression: `SUM(delivered_lines.is_otif) / NULLIF(SUM(delivered_lines.is_delivered), 0)`
- Owner VP Supply Chain; steward Supply Chain Analytics Lead; version 1, approved

## Unit fill rate (`unit_fill_rate`)

Share of ordered units that left on the first shipment, dated by the customer's requested date.

- Formula: SUM(first_shipment_qty) / SUM(ordered_qty), lines dated by requested_date, cancelled excluded.
- Numerator: Units on the first shipment of non-cancelled lines requested in the period.
- Denominator: Units ordered on non-cancelled lines requested in the period.
- Grain sales_order_line; dated by requested_date; window period; unit ratio
- Expression: `SUM(requested_lines.live_first_qty) / NULLIF(SUM(requested_lines.live_ordered_qty), 0)`
- Owner VP Supply Chain; steward Demand Planning Manager; version 1, approved

## Line fill rate (`line_fill_rate`), variant of `unit_fill_rate`

Share of order lines filled completely on the first shipment.

- Formula: SUM(is_line_filled) / SUM(is_live), dated by requested_date.
- Numerator: Non-cancelled lines whose first shipment covered the ordered quantity.
- Denominator: Non-cancelled lines requested in the period.
- Grain sales_order_line; dated by requested_date; window period; unit ratio
- Expression: `SUM(requested_lines.is_line_filled) / NULLIF(SUM(requested_lines.is_live), 0)`
- Owner VP Supply Chain; steward Demand Planning Manager; version 1, approved

## Order fill rate (`order_fill_rate`), variant of `unit_fill_rate`

Share of orders where every line was filled completely on the first shipment.

- Formula: SUM(is_order_filled) / SUM(is_order_head), counted once per order on its first live line.
- Numerator: Orders where every non-cancelled line was filled on the first shipment.
- Denominator: Orders with at least one non-cancelled line requested in the period.
- Grain sales_order; dated by requested_date; window period; unit ratio
- Expression: `SUM(requested_lines.is_order_filled) / NULLIF(SUM(requested_lines.is_order_head), 0)`
- Owner VP Supply Chain; steward Demand Planning Manager; version 1, approved

## Days of inventory (`days_of_inventory`)

How many days the month-end on-hand stock would last at the trailing 90-day rate of shipments.

- Formula: SUM(on_hand_value_end) / (SUM(cogs_90d) / 90), ratio of sums at the requested grouping.
- Numerator: On-hand value at standard cost on the last snapshot of the period.
- Denominator: Trailing 90-day cost of goods shipped, divided by 90.
- Grain storage_location_part; dated by snapshot_date; window point_in_time; unit days
- Expression: `SUM(inventory.on_hand_value_end) / NULLIF(SUM(inventory.cogs_daily_90d), 0)`
- Owner VP Supply Chain; steward Inventory Manager; version 1, approved

## Days of inventory in units (`doi_units`), variant of `days_of_inventory`

Days of inventory measured in units rather than value.

- Formula: SUM(on_hand_qty_end) / (SUM(units_90d) / 90).
- Numerator: On-hand units on the last snapshot of the period.
- Denominator: Trailing 90-day units shipped, divided by 90.
- Grain storage_location_part; dated by snapshot_date; window point_in_time; unit days
- Expression: `SUM(inventory.on_hand_qty_end) / NULLIF(SUM(inventory.units_daily_90d), 0)`
- Owner VP Supply Chain; steward Inventory Manager; version 1, approved

## Days inventory outstanding (finance) (`dio_financial`), variant of `days_of_inventory`

Days inventory outstanding on the finance basis, average inventory over cost of sales times days in the period.

- Formula: SUM(avg_inventory_value * days_in_period) / SUM(cost_of_sales).
- Numerator: Average daily on-hand value over the month, times days in the month.
- Denominator: Cost of goods shipped in the month.
- Grain storage_location_part; dated by snapshot_date; window period; unit days
- Expression: `SUM(inventory.avg_value_x_days) / NULLIF(SUM(inventory.cogs_month), 0)`
- Owner Finance; steward Financial Planning Lead; version 1, approved

## Inventory turns (`inventory_turns`)

How many times a year the month-end stock turns over at the trailing 90-day shipment rate.

- Formula: (SUM(cogs_90d) / 90 * 365) / SUM(on_hand_value_end); inventory_turns x days_of_inventory = 365.
- Numerator: Trailing 90-day cost of goods shipped, annualised (divided by 90, times 365).
- Denominator: On-hand value at standard cost on the last snapshot of the period.
- Grain storage_location_part; dated by snapshot_date; window trailing_90_days; unit turns_per_year
- Expression: `SUM(inventory.cogs_annual_90d) / NULLIF(SUM(inventory.on_hand_value_end), 0)`
- Owner VP Supply Chain; steward Inventory Manager; version 1, approved

## Stockout rate (`stockout_rate`)

Share of location-part-days with demand allocated but nothing on hand.

- Formula: SUM(stockout_days) / SUM(obs_days).
- Numerator: Location-part-days with zero on hand and allocated demand.
- Denominator: Location-part-days observed in the period.
- Grain storage_location_part; dated by snapshot_date; window period; unit ratio
- Expression: `SUM(inventory.stockout_days) / NULLIF(SUM(inventory.obs_days), 0)`
- Owner VP Supply Chain; steward Inventory Manager; version 1, approved

## Landed cost per unit (`landed_cost_per_unit`)

Fully loaded USD cost of each received unit, weighted by received quantity.

- Formula: SUM(material + freight + duty + insurance + handling) / SUM(received_qty), dated by receipt_date.
- Numerator: Material (unit cost x received qty x FX at PO date) + inbound freight by chargeable-weight share + duty at the rate in force on the ship date x customs value + insurance + handling.
- Denominator: Units received in the period.
- Grain purchase_order_line; dated by receipt_date; window period; unit usd_per_unit
- Expression: `SUM(po_lines.landed_usd) / NULLIF(SUM(po_lines.received_qty), 0)`
- Owner VP Procurement; steward Procurement Analytics Lead; version 1, approved

## Supplier lead time (`supplier_lead_time_days`)

Median calendar days from placing a purchase order line to receiving it.

- Formula: MEDIAN(receipt_date - order_date) over received lines, dated by receipt_date.
- Numerator: Calendar days from PO date to goods receipt, received lines only.
- Denominator: not applicable (median)
- Grain purchase_order_line; dated by receipt_date; window period; unit days
- Expression: `MEDIAN(po_lines.lead_days)`
- Owner VP Procurement; steward Procurement Analytics Lead; version 1, approved

## Lead time variability (`lead_time_variability`)

Sample standard deviation of supplier lead time in days; how far a planner can trust the median.

- Formula: STDDEV_SAMP(receipt_date - order_date) over received lines, dated by receipt_date.
- Numerator: Calendar days from PO date to goods receipt, received lines only.
- Denominator: not applicable (sample standard deviation)
- Grain purchase_order_line; dated by receipt_date; window period; unit days
- Expression: `STDDEV_SAMP(po_lines.lead_days)`
- Owner VP Procurement; steward Procurement Analytics Lead; version 1, approved

## Order fulfilment cycle time (`order_fulfilment_cycle_days`)

Median calendar days from a customer placing an order line to receiving it.

- Formula: MEDIAN(actual_delivery_date - order_date), dated by actual_delivery_date.
- Numerator: Calendar days from order date to actual delivery, delivered lines only.
- Denominator: not applicable (median)
- Grain sales_order_line; dated by actual_delivery_date; window period; unit days
- Expression: `MEDIAN(delivered_lines.cycle_days)`
- Owner VP Supply Chain; steward Supply Chain Analytics Lead; version 1, approved

## Transit time (`transit_hours`)

Median hours a delivered shipment spent between pick-up and proof of delivery.

- Formula: MEDIAN(delivered_utc - picked_up_utc) in hours, dated by actual_delivery.
- Numerator: Hours from the picked_up event to the delivered event, both in UTC.
- Denominator: not applicable (median)
- Grain shipment; dated by actual_delivery; window period; unit hours
- Expression: `MEDIAN(shipments.transit_hours_elapsed)`
- Owner VP Logistics; steward Logistics Analytics Lead; version 1, approved

## Freight cost per unit (`freight_cost_per_unit`)

Outbound freight cost in USD for each unit shipped, weighted by units.

- Formula: SUM(freight_alloc_usd) / SUM(shipped_qty), dated by ship_date.
- Numerator: Outbound freight in USD allocated to each shipment line by chargeable-weight share.
- Denominator: Units shipped.
- Grain shipment_line; dated by ship_date; window period; unit usd_per_unit
- Expression: `SUM(shipment_lines.freight_alloc_usd) / NULLIF(SUM(shipment_lines.shipped_qty), 0)`
- Owner VP Logistics; steward Logistics Analytics Lead; version 1, approved

## Landed cost components

`landed_usd` in fct_po_line is material (unit cost x received qty x FX on the PO date) + inbound
freight shared by received weight + duty + insurance (0.004 x material) + handling (USD 0.12 per unit). Duty is the per-part rate from
erp/material_tariffs in force on the inbound shipment's depart date, times material value, for
imports only. The rate table comes from the data generator; HTS_2026 is reference data and is not
read by the model.
