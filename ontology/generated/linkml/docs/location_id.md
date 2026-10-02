---
search:
  boost: 5.0
---

# Slot: location_id 


_Identifier of the event location._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/location_id](https://scm-ontology.example.com/schema/location_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DeliveryEvent](DeliveryEvent.md) | A timestamped event in the lifecycle of a shipment |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [DeliveryEvent](DeliveryEvent.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [DeliveryEvent](DeliveryEvent.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/location_id |
| native | https://scm-ontology.example.com/schema/location_id |




## LinkML Source

<details>
```yaml
name: location_id
description: Identifier of the event location.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: DeliveryEvent
domain_of:
- DeliveryEvent
range: string

```
</details></div>