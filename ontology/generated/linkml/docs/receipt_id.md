---
search:
  boost: 5.0
---

# Slot: receipt_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/receipt_id](https://scm-ontology.example.com/schema/receipt_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [GoodsReceipt](GoodsReceipt.md) | A record of parts received against a purchase order line |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [GoodsReceipt](GoodsReceipt.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |
| Owner | [GoodsReceipt](GoodsReceipt.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/receipt_id |
| native | https://scm-ontology.example.com/schema/receipt_id |




## LinkML Source

<details>
```yaml
name: receipt_id
from_schema: https://scm-ontology.example.com/schema
rank: 1000
identifier: true
owner: GoodsReceipt
domain_of:
- GoodsReceipt
range: string
required: true

```
</details></div>