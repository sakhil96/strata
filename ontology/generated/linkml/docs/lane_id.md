---
search:
  boost: 5.0
---

# Slot: lane_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/lane_id](https://scm-ontology.example.com/schema/lane_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Shipment](Shipment.md) | A transport movement from origin to destination |  no  |
| [Lane](Lane.md) | A defined transportation route between an origin and destination |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Shipment](Shipment.md), [Lane](Lane.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/lane_id |
| native | https://scm-ontology.example.com/schema/lane_id |




## LinkML Source

<details>
```yaml
name: lane_id
domain_of:
- Shipment
- Lane
range: string

```
</details></div>