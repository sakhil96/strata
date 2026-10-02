cube(`Part`, {
  sql: `SELECT * FROM part`,

  dimensions: {
    part_id: { sql: `part_id`, type: `string` }
    part_name: { sql: `part_name`, type: `string` }
    part_family: { sql: `part_family`, type: `string` }
    category: { sql: `category`, type: `string` }
    base_uom: { sql: `base_uom`, type: `string` }
    pack_factor: { sql: `pack_factor`, type: `string` }
    pallet_factor: { sql: `pallet_factor`, type: `string` }
    weight_kg: { sql: `weight_kg`, type: `string` }
    source_systems: { sql: `source_systems`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
