---
search:
  boost: 5.0
---

# Slot: actual_ship_date 


_Date the shipment left the warehouse._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/actual_ship_date](https://scm-ontology.example.com/schema/actual_ship_date)
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
| self | https://scm-ontology.example.com/schema/actual_ship_date |
| native | https://scm-ontology.example.com/schema/actual_ship_date |




## LinkML Source

<details>
```yaml
name: actual_ship_date
description: Date the shipment left the warehouse.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: SalesOrderLine
domain_of:
- SalesOrderLine
range: date

```
</details></div>