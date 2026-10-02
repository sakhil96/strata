cube(`GoodsReceipt`, {
  sql: `SELECT * FROM goodsreceipt`,

  dimensions: {
    receipt_id: { sql: `receipt_id`, type: `string` }
    po_line_id: { sql: `po_line_id`, type: `string` }
    receipt_date: { sql: `receipt_date`, type: `time` }
    quality_status: { sql: `quality_status`, type: `string` }
    inspector_name: { sql: `inspector_name`, type: `string` }
  },

  measures: {
    count: { type: `count` },
    received_qty: { sql: `received_qty`, type: `number` }
  }
});
