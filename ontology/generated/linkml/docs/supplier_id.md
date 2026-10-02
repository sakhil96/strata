---
search:
  boost: 5.0
---

# Slot: supplier_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/supplier_id](https://scm-ontology.example.com/schema/supplier_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Supplier](Supplier.md) | An organisation that supplies parts under contractual agreements |  no  |
| [SupplierPartAgreement](SupplierPartAgreement.md) | A contractual agreement for a supplier to supply a specific part |  no  |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Supplier](Supplier.md), [SupplierPartAgreement](SupplierPartAgreement.md), [PurchaseOrderLine](PurchaseOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/supplier_id |
| native | https://scm-ontology.example.com/schema/supplier_id |




## LinkML Source

<details>
```yaml
name: supplier_id
domain_of:
- Supplier
- SupplierPartAgreement
- PurchaseOrderLine
range: string

```
</details></div>