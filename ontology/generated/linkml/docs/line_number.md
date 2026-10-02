---
search:
  boost: 5.0
---

# Slot: line_number 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/line_number](https://scm-ontology.example.com/schema/line_number)
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
| self | https://scm-ontology.example.com/schema/line_number |
| native | https://scm-ontology.example.com/schema/line_number |




## LinkML Source

<details>
```yaml
name: line_number
domain_of:
- PurchaseOrderLine
- SalesOrderLine
range: string

```
</details></div>