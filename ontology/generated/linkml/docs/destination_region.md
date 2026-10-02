---
search:
  boost: 5.0
---

# Slot: destination_region 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/destination_region](https://scm-ontology.example.com/schema/destination_region)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Lane](Lane.md) | A defined transportation route between an origin and destination |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Lane](Lane.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Lane](Lane.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/destination_region |
| native | https://scm-ontology.example.com/schema/destination_region |




## LinkML Source

<details>
```yaml
name: destination_region
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Lane
domain_of:
- Lane
range: string

```
</details></div>