cube(`ShipmentLine`, {
  sql: `SELECT * FROM shipmentline`,

  dimensions: {
    shipment_line_id: { sql: `shipment_line_id`, type: `string` }
    shipment_id: { sql: `shipment_id`, type: `string` }
    so_line_id: { sql: `so_line_id`, type: `string` }
    is_first_shipment: { sql: `is_first_shipment`, type: `string` }
  },

  measures: {
    count: { type: `count` },
    shipped_qty: { sql: `shipped_qty`, type: `number` }
  }
});
