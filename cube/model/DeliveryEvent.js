cube(`DeliveryEvent`, {
  sql: `SELECT * FROM deliveryevent`,

  dimensions: {
    event_id: { sql: `event_id`, type: `string` }
    shipment_id: { sql: `shipment_id`, type: `string` }
    event_type: { sql: `event_type`, type: `string` }
    event_time_utc: { sql: `event_time_utc`, type: `time` }
    site_tz: { sql: `site_tz`, type: `string` }
    location_id: { sql: `location_id`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
