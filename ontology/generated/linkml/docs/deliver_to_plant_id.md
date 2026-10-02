---
search:
  boost: 5.0
---

# Slot: deliver_to_plant_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/deliver_to_plant_id](https://scm-ontology.example.com/schema/deliver_to_plant_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Plant](Plant.md) |
| Domain Of | [PurchaseOrderLine](PurchaseOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PurchaseOrderLine](PurchaseOrderLine.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/deliver_to_plant_id |
| native | https://scm-ontology.example.com/schema/deliver_to_plant_id |




## LinkML Source

<details>
```yaml
name: deliver_to_plant_id
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: PurchaseOrderLine
domain_of:
- PurchaseOrderLine
range: Plant

```
</details></div>