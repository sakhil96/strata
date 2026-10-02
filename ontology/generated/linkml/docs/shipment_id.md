---
search:
  boost: 5.0
---

# Slot: shipment_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/shipment_id](https://scm-ontology.example.com/schema/shipment_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Shipment](Shipment.md) | A transport movement from origin to destination |  no  |
| [ShipmentLine](ShipmentLine.md) | Links a sales order line to a shipment with the shipped quantity |  no  |
| [DeliveryEvent](DeliveryEvent.md) | A timestamped event in the lifecycle of a shipment |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Shipment](Shipment.md), [ShipmentLine](ShipmentLine.md), [DeliveryEvent](DeliveryEvent.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/shipment_id |
| native | https://scm-ontology.example.com/schema/shipment_id |




## LinkML Source

<details>
```yaml
name: shipment_id
domain_of:
- Shipment
- ShipmentLine
- DeliveryEvent
range: string

```
</details></div>