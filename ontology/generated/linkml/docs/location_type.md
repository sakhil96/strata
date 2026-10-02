---
search:
  boost: 5.0
---

# Slot: location_type 


_RACK, BULK, COLD, YARD._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/location_type](https://scm-ontology.example.com/schema/location_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [StorageLocation](StorageLocation.md) | A named location within a plant where inventory is held |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [StorageLocation](StorageLocation.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [StorageLocation](StorageLocation.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/location_type |
| native | https://scm-ontology.example.com/schema/location_type |




## LinkML Source

<details>
```yaml
name: location_type
description: RACK, BULK, COLD, YARD.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: StorageLocation
domain_of:
- StorageLocation
range: string

```
</details></div>