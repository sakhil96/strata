cube(`Plant`, {
  sql: `SELECT * FROM plant`,

  dimensions: {
    plant_id: { sql: `plant_id`, type: `string` }
    plant_name: { sql: `plant_name`, type: `string` }
    plant_type: { sql: `plant_type`, type: `string` }
    region: { sql: `region`, type: `string` }
    country_code: { sql: `country_code`, type: `string` }
    timezone: { sql: `timezone`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
