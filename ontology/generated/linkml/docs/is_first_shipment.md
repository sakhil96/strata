---
search:
  boost: 5.0
---

# Slot: is_first_shipment 


_True if this is the first shipment against the sales order line._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/is_first_shipment](https://scm-ontology.example.com/schema/is_first_shipment)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ShipmentLine](ShipmentLine.md) | Links a sales order line to a shipment with the shipped quantity |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [ShipmentLine](ShipmentLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [ShipmentLine](ShipmentLine.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/is_first_shipment |
| native | https://scm-ontology.example.com/schema/is_first_shipment |




## LinkML Source

<details>
```yaml
name: is_first_shipment
description: True if this is the first shipment against the sales order line.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: ShipmentLine
domain_of:
- ShipmentLine
range: boolean

```
</details></div>