---
search:
  boost: 5.0
---

# Slot: bank_account 


_Bank account number for payments._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/bank_account](https://scm-ontology.example.com/schema/bank_account)
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



### Annotations

| property | value |
| --- | --- |
| sensitivity | RESTRICTED |




### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/bank_account |
| native | https://scm-ontology.example.com/schema/bank_account |




## LinkML Source

<details>
```yaml
name: bank_account
annotations:
  sensitivity:
    tag: sensitivity
    value: RESTRICTED
description: Bank account number for payments.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: Supplier
domain_of:
- Supplier
range: string

```
</details></div>