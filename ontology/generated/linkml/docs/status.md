---
search:
  boost: 5.0
---

# Slot: status 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/status](https://scm-ontology.example.com/schema/status)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |
| [Shipment](Shipment.md) | A transport movement from origin to destination |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [PurchaseOrderLine](PurchaseOrderLine.md), [SalesOrderLine](SalesOrderLine.md), [Shipment](Shipment.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/status |
| native | https://scm-ontology.example.com/schema/status |




## LinkML Source

<details>
```yaml
name: status
domain_of:
- PurchaseOrderLine
- SalesOrderLine
- Shipment
range: string

```
</details></div>