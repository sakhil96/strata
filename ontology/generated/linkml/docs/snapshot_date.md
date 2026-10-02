---
search:
  boost: 5.0
---

# Slot: snapshot_date 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/snapshot_date](https://scm-ontology.example.com/schema/snapshot_date)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [InventorySnapshot](InventorySnapshot.md) | A daily snapshot of inventory at a storage location for a part |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
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
| self | https://scm-ontology.example.com/schema/snapshot_date |
| native | https://scm-ontology.example.com/schema/snapshot_date |




## LinkML Source

<details>
```yaml
name: snapshot_date
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: InventorySnapshot
domain_of:
- InventorySnapshot
range: date

```
</details></div>