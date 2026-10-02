---
search:
  boost: 5.0
---

# Slot: po_line_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/po_line_id](https://scm-ontology.example.com/schema/po_line_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |
| [GoodsReceipt](GoodsReceipt.md) | A record of parts received against a purchase order line |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [PurchaseOrderLine](PurchaseOrderLine.md), [GoodsReceipt](GoodsReceipt.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/po_line_id |
| native | https://scm-ontology.example.com/schema/po_line_id |




## LinkML Source

<details>
```yaml
name: po_line_id
domain_of:
- PurchaseOrderLine
- GoodsReceipt
range: string

```
</details></div>