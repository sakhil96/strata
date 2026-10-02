cube(`FxRate`, {
  sql: `SELECT * FROM fxrate`,

  dimensions: {
    fx_date: { sql: `fx_date`, type: `time` }
    from_currency: { sql: `from_currency`, type: `string` }
    to_currency: { sql: `to_currency`, type: `string` }
    rate: { sql: `rate`, type: `string` }
  },

  measures: {
    count: { type: `count` },

  }
});
