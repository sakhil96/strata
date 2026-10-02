cube(`Carrier`, {
  sql: `SELECT * FROM carrier`,

  dimensions: {
    carrier_id: { sql: `carrier_id`, type: `string` }
    carrier_name: { sql: `carrier_name`, type: `string` }
    carrier_type: { sql: `carrier_type`, type: `string` }
    scac_code: { sql: `scac_code`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
