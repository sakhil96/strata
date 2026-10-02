---
search:
  boost: 5.0
---

# Slot: unit_price 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/unit_price](https://scm-ontology.example.com/schema/unit_price)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
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
| self | https://scm-ontology.example.com/schema/unit_price |
| native | https://scm-ontology.example.com/schema/unit_price |




## LinkML Source

<details>
```yaml
name: unit_price
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: SalesOrderLine
domain_of:
- SalesOrderLine
range: float

```
</details></div>