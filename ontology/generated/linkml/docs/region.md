---
search:
  boost: 5.0
---

# Slot: region 


_Geographic region (US, EMEA, APAC)._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/region](https://scm-ontology.example.com/schema/region)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Plant](Plant.md) | A manufacturing or distribution facility |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Plant](Plant.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Plant](Plant.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/region |
| native | https://scm-ontology.example.com/schema/region |




## LinkML Source

<details>
```yaml
name: region
description: Geographic region (US, EMEA, APAC).
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Plant
domain_of:
- Plant
range: string

```
</details></div>