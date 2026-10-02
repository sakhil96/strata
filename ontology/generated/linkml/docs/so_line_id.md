---
search:
  boost: 5.0
---

# Slot: so_line_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/so_line_id](https://scm-ontology.example.com/schema/so_line_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |
| [ShipmentLine](ShipmentLine.md) | Links a sales order line to a shipment with the shipped quantity |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [SalesOrderLine](SalesOrderLine.md), [ShipmentLine](ShipmentLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/so_line_id |
| native | https://scm-ontology.example.com/schema/so_line_id |




## LinkML Source

<details>
```yaml
name: so_line_id
domain_of:
- SalesOrderLine
- ShipmentLine
range: string

```
</details></div>