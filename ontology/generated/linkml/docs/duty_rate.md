---
search:
  boost: 5.0
---

# Slot: duty_rate 


_Ad valorem duty rate as a decimal (0.05 = 5%)._



<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/duty_rate](https://scm-ontology.example.com/schema/duty_rate)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TariffCode](TariffCode.md) | An HTS tariff classification with duty rates and effective dates |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [TariffCode](TariffCode.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [TariffCode](TariffCode.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/duty_rate |
| native | https://scm-ontology.example.com/schema/duty_rate |




## LinkML Source

<details>
```yaml
name: duty_rate
description: Ad valorem duty rate as a decimal (0.05 = 5%).
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: TariffCode
domain_of:
- TariffCode
range: float

```
</details></div>