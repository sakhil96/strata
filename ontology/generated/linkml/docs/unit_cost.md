---
search:
  boost: 5.0
---

# Slot: unit_cost 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/unit_cost](https://scm-ontology.example.com/schema/unit_cost)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SupplierPartAgreement](SupplierPartAgreement.md) | A contractual agreement for a supplier to supply a specific part |  no  |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [SupplierPartAgreement](SupplierPartAgreement.md), [PurchaseOrderLine](PurchaseOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/unit_cost |
| native | https://scm-ontology.example.com/schema/unit_cost |




## LinkML Source

<details>
```yaml
name: unit_cost
domain_of:
- SupplierPartAgreement
- PurchaseOrderLine
range: string

```
</details></div>