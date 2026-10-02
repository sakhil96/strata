---
search:
  boost: 5.0
---

# Slot: committed_date 


_Date committed to the customer._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/committed_date](https://scm-ontology.example.com/schema/committed_date)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [SalesOrderLine](SalesOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [SalesOrderLine](SalesOrderLine.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/committed_date |
| native | https://scm-ontology.example.com/schema/committed_date |




## LinkML Source

<details>
```yaml
name: committed_date
description: Date committed to the customer.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: SalesOrderLine
domain_of:
- SalesOrderLine
range: date

```
</details></div>