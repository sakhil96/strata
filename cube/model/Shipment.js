cube(`Shipment`, {
  sql: `SELECT * FROM shipment`,

  dimensions: {
    shipment_id: { sql: `shipment_id`, type: `string` }
    carrier_id: { sql: `carrier_id`, type: `string` }
    lane_id: { sql: `lane_id`, type: `string` }
    origin_plant_id: { sql: `origin_plant_id`, type: `string` }
    destination_id: { sql: `destination_id`, type: `string` }
    ship_date: { sql: `ship_date`, type: `time` }
    carrier_eta: { sql: `carrier_eta`, type: `time` }
    actual_delivery: { sql: `actual_delivery`, type: `time` }
    chargeable_weight_kg: { sql: `chargeable_weight_kg`, type: `string` }
    freight_currency: { sql: `freight_currency`, type: `string` }
    status: { sql: `status`, type: `string` }
  },

  measures: {
    count: { type: `count` },
    freight_charge: { sql: `freight_charge`, type: `number` }
  }
});
