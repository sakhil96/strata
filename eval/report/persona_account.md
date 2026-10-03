# Persona consistency on SCM_DEV

Each case run through GOVERNED_QUERY as PLANNING_ROLE, PROCUREMENT_ROLE and LOGISTICS_ROLE, each against its own semantic view. `identical` means all three returned the same rows and a semantic_query_hash equal to the local engine's.

| case | metric | breakdown | rows | semantic_query_hash | identical |
|---|---|---|---|---|---|
| pc01 | on_time_delivery | - | 1 | `c0e0370d730e7be4` | yes |
| pc02 | on_time_delivery | region | 3 | `6b5d262575056d3e` | yes |
| pc03 | on_time_delivery | - | 1 | `9ae321e0c3a1c3e8` | yes |
| pc04 | otif | period_month | 12 | `97065a079a8800ed` | yes |
| pc05 | otif | - | 1 | `a2f9de0886843880` | yes |
| pc06 | unit_fill_rate | - | 1 | `8921be13a7006a22` | yes |
| pc07 | unit_fill_rate | plant_id | 5 | `a94b6d10bc5ad0c8` | yes |
| pc08 | days_of_inventory | - | 1 | `645ed2c6b4a80c7f` | yes |
| pc09 | days_of_inventory | plant_id | 5 | `f7bf554e29d85827` | yes |
| pc10 | landed_cost_per_unit | - | 1 | `383f7f85ec5d788a` | yes |
| pc11 | landed_cost_per_unit | period_month | 12 | `40e81be56d429e47` | yes |
| pc12 | inventory_turns | category | 3 | `2c7fc57676ec57d1` | yes |
| pc13 | supplier_lead_time_days | region | 3 | `0b2e974bf5e9c695` | yes |
| pc14 | stockout_rate | - | 1 | `66f0b19855ea4e9a` | yes |
| pc15 | stockout_rate | period_month | 12 | `ece7631d7414ea07` | yes |
| pc16 | freight_cost_per_unit | carrier_type | 4 | `d1acb17e72e0607e` | yes |
| pc17 | order_fulfilment_cycle_days | - | 1 | `32e7a9c5bf52f505` | yes |
| pc18 | order_fulfilment_cycle_days | - | 1 | `a82805a3d1a941f3` | yes |
| pc19 | transit_hours | carrier_name | 12 | `636d33d0511b10fc` | yes |
| pc20 | transit_hours | - | 1 | `34581ff38643ee19` | yes |
