---
search:
  boost: 5.0
---

# Slot: quality_status 


_ACCEPTED, REJECTED, QUARANTINE._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/quality_status](https://scm-ontology.example.com/schema/quality_status)
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
| self | https://scm-ontology.example.com/schema/quality_status |
| native | https://scm-ontology.example.com/schema/quality_status |




## LinkML Source

<details>
```yaml
name: quality_status
description: ACCEPTED, REJECTED, QUARANTINE.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: GoodsReceipt
domain_of:
- GoodsReceipt
range: string

```
</details></div>