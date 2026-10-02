---
search:
  boost: 5.0
---

# Slot: supplier_name 


_Legal name of the supplier entity._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/supplier_name](https://scm-ontology.example.com/schema/supplier_name)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Supplier](Supplier.md) | An organisation that supplies parts under contractual agreements |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Supplier](Supplier.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Supplier](Supplier.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/supplier_name |
| native | https://scm-ontology.example.com/schema/supplier_name |




## LinkML Source

<details>
```yaml
name: supplier_name
description: Legal name of the supplier entity.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Supplier
domain_of:
- Supplier
range: string

```
</details></div>