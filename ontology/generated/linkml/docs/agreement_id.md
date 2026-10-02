---
search:
  boost: 5.0
---

# Slot: agreement_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/agreement_id](https://scm-ontology.example.com/schema/agreement_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SupplierPartAgreement](SupplierPartAgreement.md) | A contractual agreement for a supplier to supply a specific part |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [SupplierPartAgreement](SupplierPartAgreement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |
| Owner | [SupplierPartAgreement](SupplierPartAgreement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/agreement_id |
| native | https://scm-ontology.example.com/schema/agreement_id |




## LinkML Source

<details>
```yaml
name: agreement_id
from_schema: https://scm-ontology.example.com/schema
rank: 1000
identifier: true
owner: SupplierPartAgreement
domain_of:
- SupplierPartAgreement
range: string
required: true

```
</details></div>