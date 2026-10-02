cube(`TariffCode`, {
  sql: `SELECT * FROM tariffcode`,

  dimensions: {
    tariff_id: { sql: `tariff_id`, type: `string` }
    hts_code: { sql: `hts_code`, type: `string` }
    description: { sql: `description`, type: `string` }
    effective_from: { sql: `effective_from`, type: `time` }
    effective_to: { sql: `effective_to`, type: `time` }
    part_id: { sql: `part_id`, type: `string` }
  },

  measures: {
    count: { type: `count` },
    duty_rate: { sql: `duty_rate`, type: `number` }
  }
});
