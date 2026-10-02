---
search:
  boost: 5.0
---

# Slot: customer_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/customer_id](https://scm-ontology.example.com/schema/customer_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Customer](Customer.md) | An organisation that purchases finished goods |  no  |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Customer](Customer.md), [SalesOrderLine](SalesOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/customer_id |
| native | https://scm-ontology.example.com/schema/customer_id |




## LinkML Source

<details>
```yaml
name: customer_id
domain_of:
- Customer
- SalesOrderLine
range: string

```
</details></div>