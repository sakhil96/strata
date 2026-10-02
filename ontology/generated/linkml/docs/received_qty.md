---
search:
  boost: 5.0
---

# Slot: received_qty 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/received_qty](https://scm-ontology.example.com/schema/received_qty)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [GoodsReceipt](GoodsReceipt.md) | A record of parts received against a purchase order line |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
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
| self | https://scm-ontology.example.com/schema/received_qty |
| native | https://scm-ontology.example.com/schema/received_qty |




## LinkML Source

<details>
```yaml
name: received_qty
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: GoodsReceipt
domain_of:
- GoodsReceipt
range: float

```
</details></div>