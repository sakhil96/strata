---
search:
  boost: 5.0
---

# Slot: confirmed_date 


_Supplier-confirmed delivery date (may differ from promised)._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/confirmed_date](https://scm-ontology.example.com/schema/confirmed_date)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [PurchaseOrderLine](PurchaseOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PurchaseOrderLine](PurchaseOrderLine.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/confirmed_date |
| native | https://scm-ontology.example.com/schema/confirmed_date |




## LinkML Source

<details>
```yaml
name: confirmed_date
description: Supplier-confirmed delivery date (may differ from promised).
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: PurchaseOrderLine
domain_of:
- PurchaseOrderLine
range: date

```
</details></div>