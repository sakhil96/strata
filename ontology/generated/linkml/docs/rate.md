---
search:
  boost: 5.0
---

# Slot: rate 


_Units of to_currency per unit of from_currency._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/rate](https://scm-ontology.example.com/schema/rate)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [FxRate](FxRate.md) | A daily foreign exchange rate to USD; keyed by date and source currency |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [FxRate](FxRate.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [FxRate](FxRate.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/rate |
| native | https://scm-ontology.example.com/schema/rate |




## LinkML Source

<details>
```yaml
name: rate
description: Units of to_currency per unit of from_currency.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: FxRate
domain_of:
- FxRate
range: float

```
</details></div>