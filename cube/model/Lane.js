cube(`Lane`, {
  sql: `SELECT * FROM lane`,

  dimensions: {
    lane_id: { sql: `lane_id`, type: `string` }
    origin_region: { sql: `origin_region`, type: `string` }
    destination_region: { sql: `destination_region`, type: `string` }
    mode: { sql: `mode`, type: `string` }
    transit_days_typical: { sql: `transit_days_typical`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
