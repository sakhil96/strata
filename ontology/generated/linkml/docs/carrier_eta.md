---
search:
  boost: 5.0
---

# Slot: carrier_eta 


_Carrier-estimated arrival date._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/carrier_eta](https://scm-ontology.example.com/schema/carrier_eta)
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
| self | https://scm-ontology.example.com/schema/carrier_eta |
| native | https://scm-ontology.example.com/schema/carrier_eta |




## LinkML Source

<details>
```yaml
name: carrier_eta
description: Carrier-estimated arrival date.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Shipment
domain_of:
- Shipment
range: date

```
</details></div>