cube(`StorageLocation`, {
  sql: `SELECT * FROM storagelocation`,

  dimensions: {
    storage_location_id: { sql: `storage_location_id`, type: `string` }
    storage_location_name: { sql: `storage_location_name`, type: `string` }
    plant_id: { sql: `plant_id`, type: `string` }
    location_type: { sql: `location_type`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
