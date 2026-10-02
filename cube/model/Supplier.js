cube(`Supplier`, {
  sql: `SELECT * FROM supplier`,

  dimensions: {
    supplier_id: { sql: `supplier_id`, type: `string` }
    supplier_name: { sql: `supplier_name`, type: `string` }
    supplier_site: { sql: `supplier_site`, type: `string` }
    parent_supplier_id: { sql: `parent_supplier_id`, type: `string` }
    country_code: { sql: `country_code`, type: `string` }
    contact_name: { sql: `contact_name`, type: `string` }
    contact_email: { sql: `contact_email`, type: `string` }
    bank_account: { sql: `bank_account`, type: `string` }
    source_systems: { sql: `source_systems`, type: `string` }
    synonyms: { sql: `synonyms`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
