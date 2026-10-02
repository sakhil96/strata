---
search:
  boost: 5.0
---

# Slot: shipment_line_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/shipment_line_id](https://scm-ontology.example.com/schema/shipment_line_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ShipmentLine](ShipmentLine.md) | Links a sales order line to a shipment with the shipped quantity |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ShipmentLine](ShipmentLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |
| Owner | [ShipmentLine](ShipmentLine.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/shipment_line_id |
| native | https://scm-ontology.example.com/schema/shipment_line_id |




## LinkML Source

<details>
```yaml
name: shipment_line_id
from_schema: https://scm-ontology.example.com/schema
rank: 1000
identifier: true
owner: ShipmentLine
domain_of:
- ShipmentLine
range: string
required: true

```
</details></div>