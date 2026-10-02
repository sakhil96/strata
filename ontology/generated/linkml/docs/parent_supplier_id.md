---
search:
  boost: 5.0
---

# Slot: parent_supplier_id 


_Parent supplier in the supplier hierarchy (site > parent)._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/parent_supplier_id](https://scm-ontology.example.com/schema/parent_supplier_id)
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
| self | https://scm-ontology.example.com/schema/parent_supplier_id |
| native | https://scm-ontology.example.com/schema/parent_supplier_id |




## LinkML Source

<details>
```yaml
name: parent_supplier_id
description: Parent supplier in the supplier hierarchy (site > parent).
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Supplier
domain_of:
- Supplier
range: string

```
</details></div>