---
search:
  boost: 5.0
---

# Slot: actual_delivery 


_Actual delivery date from carrier confirmation._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/actual_delivery](https://scm-ontology.example.com/schema/actual_delivery)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Shipment](Shipment.md) | A transport movement from origin to destination |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [Shipment](Shipment.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Shipment](Shipment.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/actual_delivery |
| native | https://scm-ontology.example.com/schema/actual_delivery |




## LinkML Source

<details>
```yaml
name: actual_delivery
description: Actual delivery date from carrier confirmation.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Shipment
domain_of:
- Shipment
range: date

```
</details></div>