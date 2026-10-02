---
search:
  boost: 5.0
---

# Slot: tariff_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/tariff_id](https://scm-ontology.example.com/schema/tariff_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TariffCode](TariffCode.md) | An HTS tariff classification with duty rates and effective dates |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [TariffCode](TariffCode.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Identifier | Yes |
| Owner | [TariffCode](TariffCode.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/tariff_id |
| native | https://scm-ontology.example.com/schema/tariff_id |




## LinkML Source

<details>
```yaml
name: tariff_id
from_schema: https://scm-ontology.example.com/schema
rank: 1000
identifier: true
owner: TariffCode
domain_of:
- TariffCode
range: string
required: true

```
</details></div>