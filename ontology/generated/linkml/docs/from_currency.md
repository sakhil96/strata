---
search:
  boost: 5.0
---

# Slot: from_currency 


_ISO 4217 source currency._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/from_currency](https://scm-ontology.example.com/schema/from_currency)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [FxRate](FxRate.md) | A daily foreign exchange rate to USD; keyed by date and source currency |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
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
| self | https://scm-ontology.example.com/schema/from_currency |
| native | https://scm-ontology.example.com/schema/from_currency |




## LinkML Source

<details>
```yaml
name: from_currency
description: ISO 4217 source currency.
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: FxRate
domain_of:
- FxRate
range: string

```
</details></div>