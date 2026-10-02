---
search:
  boost: 5.0
---

# Slot: quoted_lead_days 


_Supplier-quoted lead time in calendar days._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/quoted_lead_days](https://scm-ontology.example.com/schema/quoted_lead_days)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SupplierPartAgreement](SupplierPartAgreement.md) | A contractual agreement for a supplier to supply a specific part |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [SupplierPartAgreement](SupplierPartAgreement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [SupplierPartAgreement](SupplierPartAgreement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/quoted_lead_days |
| native | https://scm-ontology.example.com/schema/quoted_lead_days |




## LinkML Source

<details>
```yaml
name: quoted_lead_days
description: Supplier-quoted lead time in calendar days.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: SupplierPartAgreement
domain_of:
- SupplierPartAgreement
range: integer

```
</details></div>