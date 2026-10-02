cube(`InventorySnapshot`, {
  sql: `SELECT * FROM inventorysnapshot`,

  dimensions: {
    snapshot_id: { sql: `snapshot_id`, type: `string` }
    storage_location_id: { sql: `storage_location_id`, type: `string` }
    part_id: { sql: `part_id`, type: `string` }
    snapshot_date: { sql: `snapshot_date`, type: `time` }
  },

  measures: {
    count: { type: `count` },
    on_hand_qty: { sql: `on_hand_qty`, type: `number` }
    on_hand_value_std: { sql: `on_hand_value_std`, type: `number` }
    in_transit_qty: { sql: `in_transit_qty`, type: `number` }
    allocated_qty: { sql: `allocated_qty`, type: `number` }
  }
});
