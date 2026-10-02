---
search:
  boost: 5.0
---

# Slot: part_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/part_id](https://scm-ontology.example.com/schema/part_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Part](Part.md) | A stock-keeping unit that can be purchased, stored, and sold |  no  |
| [SupplierPartAgreement](SupplierPartAgreement.md) | A contractual agreement for a supplier to supply a specific part |  no  |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |
| [InventorySnapshot](InventorySnapshot.md) | A daily snapshot of inventory at a storage location for a part |  no  |
| [TariffCode](TariffCode.md) | An HTS tariff classification with duty rates and effective dates |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Part](Part.md), [SupplierPartAgreement](SupplierPartAgreement.md), [PurchaseOrderLine](PurchaseOrderLine.md), [SalesOrderLine](SalesOrderLine.md), [InventorySnapshot](InventorySnapshot.md), [TariffCode](TariffCode.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/part_id |
| native | https://scm-ontology.example.com/schema/part_id |




## LinkML Source

<details>
```yaml
name: part_id
domain_of:
- Part
- SupplierPartAgreement
- PurchaseOrderLine
- SalesOrderLine
- InventorySnapshot
- TariffCode
range: string

```
</details></div>