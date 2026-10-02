---
search:
  boost: 5.0
---

# Slot: destination_id 


_Customer ship-to or inter-plant destination._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/destination_id](https://scm-ontology.example.com/schema/destination_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Shipment](Shipment.md) | A transport movement from origin to destination |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
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
| self | https://scm-ontology.example.com/schema/destination_id |
| native | https://scm-ontology.example.com/schema/destination_id |




## LinkML Source

<details>
```yaml
name: destination_id
description: Customer ship-to or inter-plant destination.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Shipment
domain_of:
- Shipment
range: string

```
</details></div>