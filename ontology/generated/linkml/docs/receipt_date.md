---
search:
  boost: 5.0
---

# Slot: receipt_date 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/receipt_date](https://scm-ontology.example.com/schema/receipt_date)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [GoodsReceipt](GoodsReceipt.md) | A record of parts received against a purchase order line |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Date](Date.md) |
| Domain Of | [GoodsReceipt](GoodsReceipt.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [GoodsReceipt](GoodsReceipt.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/receipt_date |
| native | https://scm-ontology.example.com/schema/receipt_date |




## LinkML Source

<details>
```yaml
name: receipt_date
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: GoodsReceipt
domain_of:
- GoodsReceipt
range: date

```
</details></div>