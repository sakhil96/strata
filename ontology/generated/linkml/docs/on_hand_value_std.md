---
search:
  boost: 5.0
---

# Slot: on_hand_value_std 


_On-hand value in standard cost (USD)._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/on_hand_value_std](https://scm-ontology.example.com/schema/on_hand_value_std)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [InventorySnapshot](InventorySnapshot.md) | A daily snapshot of inventory at a storage location for a part |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [InventorySnapshot](InventorySnapshot.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [InventorySnapshot](InventorySnapshot.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/on_hand_value_std |
| native | https://scm-ontology.example.com/schema/on_hand_value_std |




## LinkML Source

<details>
```yaml
name: on_hand_value_std
description: On-hand value in standard cost (USD).
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: InventorySnapshot
domain_of:
- InventorySnapshot
range: float

```
</details></div>