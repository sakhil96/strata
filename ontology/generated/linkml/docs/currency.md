---
search:
  boost: 5.0
---

# Slot: currency 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/currency](https://scm-ontology.example.com/schema/currency)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SupplierPartAgreement](SupplierPartAgreement.md) | A contractual agreement for a supplier to supply a specific part |  no  |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [SupplierPartAgreement](SupplierPartAgreement.md), [PurchaseOrderLine](PurchaseOrderLine.md), [SalesOrderLine](SalesOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/currency |
| native | https://scm-ontology.example.com/schema/currency |




## LinkML Source

<details>
```yaml
name: currency
domain_of:
- SupplierPartAgreement
- PurchaseOrderLine
- SalesOrderLine
range: string

```
</details></div>