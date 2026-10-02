---
search:
  boost: 5.0
---

# Slot: carrier_type 


_OCEAN, AIR, ROAD, RAIL, PARCEL._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/carrier_type](https://scm-ontology.example.com/schema/carrier_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Carrier](Carrier.md) | A freight carrier or logistics service provider |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Carrier](Carrier.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Carrier](Carrier.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/carrier_type |
| native | https://scm-ontology.example.com/schema/carrier_type |




## LinkML Source

<details>
```yaml
name: carrier_type
description: OCEAN, AIR, ROAD, RAIL, PARCEL.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Carrier
domain_of:
- Carrier
range: string

```
</details></div>