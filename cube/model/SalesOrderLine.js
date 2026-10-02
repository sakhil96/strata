cube(`SalesOrderLine`, {
  sql: `SELECT * FROM salesorderline`,

  dimensions: {
    so_line_id: { sql: `so_line_id`, type: `string` }
    so_number: { sql: `so_number`, type: `string` }
    line_number: { sql: `line_number`, type: `string` }
    customer_id: { sql: `customer_id`, type: `string` }
    part_id: { sql: `part_id`, type: `string` }
    fulfilled_from_location_id: { sql: `fulfilled_from_location_id`, type: `string` }
    currency: { sql: `currency`, type: `string` }
    requested_date: { sql: `requested_date`, type: `time` }
    committed_date: { sql: `committed_date`, type: `time` }
    actual_ship_date: { sql: `actual_ship_date`, type: `time` }
    actual_delivery_date: { sql: `actual_delivery_date`, type: `time` }
    status: { sql: `status`, type: `string` }
  },

  measures: {
    count: { type: `count` },
    ordered_qty: { sql: `ordered_qty`, type: `number` }
    unit_price: { sql: `unit_price`, type: `number` }
  }
});
