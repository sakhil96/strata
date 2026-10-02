---
search:
  boost: 5.0
---

# Slot: order_date 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/order_date](https://scm-ontology.example.com/schema/order_date)
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
| self | https://scm-ontology.example.com/schema/order_date |
| native | https://scm-ontology.example.com/schema/order_date |




## LinkML Source

<details>
```yaml
name: order_date
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: PurchaseOrderLine
domain_of:
- PurchaseOrderLine
range: date

```
</details></div>