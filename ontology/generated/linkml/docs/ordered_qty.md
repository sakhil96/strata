---
search:
  boost: 5.0
---

# Slot: ordered_qty 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/ordered_qty](https://scm-ontology.example.com/schema/ordered_qty)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [PurchaseOrderLine](PurchaseOrderLine.md), [SalesOrderLine](SalesOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/ordered_qty |
| native | https://scm-ontology.example.com/schema/ordered_qty |




## LinkML Source

<details>
```yaml
name: ordered_qty
domain_of:
- PurchaseOrderLine
- SalesOrderLine
range: string

```
</details></div>