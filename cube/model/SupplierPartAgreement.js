cube(`SupplierPartAgreement`, {
  sql: `SELECT * FROM supplierpartagreement`,

  dimensions: {
    agreement_id: { sql: `agreement_id`, type: `string` }
    supplier_id: { sql: `supplier_id`, type: `string` }
    part_id: { sql: `part_id`, type: `string` }
    currency: { sql: `currency`, type: `string` }
    incoterm: { sql: `incoterm`, type: `string` }
    quoted_lead_days: { sql: `quoted_lead_days`, type: `string` }
    effective_from: { sql: `effective_from`, type: `time` }
    effective_to: { sql: `effective_to`, type: `time` }
  },

  measures: {
    count: { type: `count` },
    unit_cost: { sql: `unit_cost`, type: `number` }
  }
});
