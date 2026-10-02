cube(`Customer`, {
  sql: `SELECT * FROM customer`,

  dimensions: {
    customer_id: { sql: `customer_id`, type: `string` }
    customer_name: { sql: `customer_name`, type: `string` }
    ship_to_id: { sql: `ship_to_id`, type: `string` }
    sold_to_id: { sql: `sold_to_id`, type: `string` }
    account_id: { sql: `account_id`, type: `string` }
    segment: { sql: `segment`, type: `string` }
    country_code: { sql: `country_code`, type: `string` }
    contact_name: { sql: `contact_name`, type: `string` }
    contact_email: { sql: `contact_email`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
