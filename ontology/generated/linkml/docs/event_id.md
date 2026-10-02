---
search:
  boost: 5.0
---

# Slot: event_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/event_id](https://scm-ontology.example.com/schema/event_id)
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
| Required | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |
| Owner | [DeliveryEvent](DeliveryEvent.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/event_id |
| native | https://scm-ontology.example.com/schema/event_id |




## LinkML Source

<details>
```yaml
name: event_id
from_schema: https://scm-ontology.example.com/schema
rank: 1000
identifier: true
owner: DeliveryEvent
domain_of:
- DeliveryEvent
range: string
required: true

```
</details></div>