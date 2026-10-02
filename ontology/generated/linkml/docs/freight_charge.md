---
search:
  boost: 5.0
---

# Slot: freight_charge 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/freight_charge](https://scm-ontology.example.com/schema/freight_charge)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Shipment](Shipment.md) | A transport movement from origin to destination |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [Shipment](Shipment.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Shipment](Shipment.md) |












## Identifier and Mapping Information



### Annotations

| property | value |
| --- | --- |
| sensitivity | RESTRICTED |




### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/freight_charge |
| native | https://scm-ontology.example.com/schema/freight_charge |




## LinkML Source

<details>
```yaml
name: freight_charge
annotations:
  sensitivity:
    tag: sensitivity
    value: RESTRICTED
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Shipment
domain_of:
- Shipment
range: float

```
</details></div>