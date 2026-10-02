cube(`PurchaseOrderLine`, {
  sql: `SELECT * FROM purchaseorderline`,

  dimensions: {
    po_line_id: { sql: `po_line_id`, type: `string` }
    po_number: { sql: `po_number`, type: `string` }
    line_number: { sql: `line_number`, type: `string` }
    supplier_id: { sql: `supplier_id`, type: `string` }
    part_id: { sql: `part_id`, type: `string` }
    deliver_to_plant_id: { sql: `deliver_to_plant_id`, type: `string` }
    currency: { sql: `currency`, type: `string` }
    order_date: { sql: `order_date`, type: `time` }
    promised_date: { sql: `promised_date`, type: `time` }
    confirmed_date: { sql: `confirmed_date`, type: `time` }
    status: { sql: `status`, type: `string` }
  },

  measures: {
    count: { type: `count` },
    ordered_qty: { sql: `ordered_qty`, type: `number` }
    unit_cost: { sql: `unit_cost`, type: `number` }
  }
});
