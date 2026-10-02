---
search:
  boost: 5.0
---

# Slot: fulfilled_from_location_id 

<div data-search-exclude markdown="1">



URI: [https://scm-ontology.example.com/schema/fulfilled_from_location_id](https://scm-ontology.example.com/schema/fulfilled_from_location_id)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [StorageLocation](StorageLocation.md) |
| Domain Of | [SalesOrderLine](SalesOrderLine.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [SalesOrderLine](SalesOrderLine.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://scm-ontology.example.com/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | https://scm-ontology.example.com/schema/fulfilled_from_location_id |
| native | https://scm-ontology.example.com/schema/fulfilled_from_location_id |




## LinkML Source

<details>
```yaml
name: fulfilled_from_location_id
from_schema: https://scm-ontology.example.com/schema
rank: 1000
owner: SalesOrderLine
domain_of:
- SalesOrderLine
range: StorageLocation

```
</details></div>