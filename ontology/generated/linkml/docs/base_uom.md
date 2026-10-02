---
search:
  boost: 5.0
---

# Slot: base_uom 


_Base unit of measure (each, kg, litre)._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/base_uom](https://scm-ontology.example.com/schema/base_uom)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Part](Part.md) | A stock-keeping unit that can be purchased, stored, and sold |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Part](Part.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Part](Part.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/base_uom |
| native | https://scm-ontology.example.com/schema/base_uom |




## LinkML Source

<details>
```yaml
name: base_uom
description: Base unit of measure (each, kg, litre).
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Part
domain_of:
- Part
range: string

```
</details></div>