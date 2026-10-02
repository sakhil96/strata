---
search:
  boost: 5.0
---

# Slot: carrier_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/carrier_id](https://scm-ontology.example.com/schema/carrier_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Shipment](Shipment.md) | A transport movement from origin to destination |  no  |
| [Carrier](Carrier.md) | A freight carrier or logistics service provider |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Shipment](Shipment.md), [Carrier](Carrier.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/carrier_id |
| native | https://scm-ontology.example.com/schema/carrier_id |




## LinkML Source

<details>
```yaml
name: carrier_id
domain_of:
- Shipment
- Carrier
range: string

```
</details></div>