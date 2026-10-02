---
search:
  boost: 5.0
---

# Slot: storage_location_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/storage_location_id](https://scm-ontology.example.com/schema/storage_location_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [StorageLocation](StorageLocation.md) | A named location within a plant where inventory is held |  no  |
| [InventorySnapshot](InventorySnapshot.md) | A daily snapshot of inventory at a storage location for a part |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [StorageLocation](StorageLocation.md), [InventorySnapshot](InventorySnapshot.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/storage_location_id |
| native | https://scm-ontology.example.com/schema/storage_location_id |




## LinkML Source

<details>
```yaml
name: storage_location_id
domain_of:
- StorageLocation
- InventorySnapshot
range: string

```
</details></div>