---
search:
  boost: 5.0
---

# Slot: shipped_qty 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/shipped_qty](https://scm-ontology.example.com/schema/shipped_qty)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ShipmentLine](ShipmentLine.md) | Links a sales order line to a shipment with the shipped quantity |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
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
| self | https://scm-ontology.example.com/schema/shipped_qty |
| native | https://scm-ontology.example.com/schema/shipped_qty |




## LinkML Source

<details>
```yaml
name: shipped_qty
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: ShipmentLine
domain_of:
- ShipmentLine
range: float

```
</details></div>