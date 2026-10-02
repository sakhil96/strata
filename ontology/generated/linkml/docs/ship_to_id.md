---
search:
  boost: 5.0
---

# Slot: ship_to_id 


_Ship-to location in the Customer hierarchy._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/ship_to_id](https://scm-ontology.example.com/schema/ship_to_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Customer](Customer.md) | An organisation that purchases finished goods |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Customer](Customer.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Customer](Customer.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/ship_to_id |
| native | https://scm-ontology.example.com/schema/ship_to_id |




## LinkML Source

<details>
```yaml
name: ship_to_id
description: Ship-to location in the Customer hierarchy.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Customer
domain_of:
- Customer
range: string

```
</details></div>