---
search:
  boost: 5.0
---

# Slot: synonyms 


_Alternative names (vendor, seller)._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/synonyms](https://scm-ontology.example.com/schema/synonyms)
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
| Multivalued | Yes |
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
| self | https://scm-ontology.example.com/schema/synonyms |
| native | https://scm-ontology.example.com/schema/synonyms |




## LinkML Source

<details>
```yaml
name: synonyms
description: Alternative names (vendor, seller).
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Supplier
domain_of:
- Supplier
range: string
multivalued: true

```
</details></div>