# Supply Chain Ontology

An enterprise supply chain ontology covering procurement, logistics, inventory and sales order fulfilment. Entities map to the IOF Supply Chain Reference Ontology where a class exists.

URI: https://scm-ontology.example.com/schema

Name: scm_ontology



## Classes

| Class | Description |
| --- | --- |
| [Carrier](Carrier.md) | A freight carrier or logistics service provider |
| [Customer](Customer.md) | An organisation that purchases finished goods |
| [DeliveryEvent](DeliveryEvent.md) | A timestamped event in the lifecycle of a shipment |
| [FxRate](FxRate.md) | A daily foreign exchange rate to USD; keyed by date and source currency |
| [GoodsReceipt](GoodsReceipt.md) | A record of parts received against a purchase order line |
| [InventorySnapshot](InventorySnapshot.md) | A daily snapshot of inventory at a storage location for a part |
| [Lane](Lane.md) | A defined transportation route between an origin and destination |
| [Part](Part.md) | A stock-keeping unit that can be purchased, stored, and sold |
| [Plant](Plant.md) | A manufacturing or distribution facility |
| [PurchaseOrderLine](PurchaseOrderLine.md) | A line on a purchase order placed with a supplier |
| [SalesOrderLine](SalesOrderLine.md) | A line on a customer sales order |
| [Shipment](Shipment.md) | A transport movement from origin to destination |
| [ShipmentLine](ShipmentLine.md) | Links a sales order line to a shipment with the shipped quantity |
| [StorageLocation](StorageLocation.md) | A named location within a plant where inventory is held |
| [Supplier](Supplier.md) | An organisation that supplies parts under contractual agreements |
| [SupplierPartAgreement](SupplierPartAgreement.md) | A contractual agreement for a supplier to supply a specific part |
| [TariffCode](TariffCode.md) | An HTS tariff classification with duty rates and effective dates |



## Slots

| Slot | Description |
| --- | --- |
| [account_id](account_id.md) | Account in the hierarchy |
| [actual_delivery](actual_delivery.md) | Actual delivery date from carrier confirmation |
| [actual_delivery_date](actual_delivery_date.md) | Date confirmed delivered to the customer |
| [actual_ship_date](actual_ship_date.md) | Date the shipment left the warehouse |
| [agreement_id](agreement_id.md) |  |
| [allocated_qty](allocated_qty.md) |  |
| [bank_account](bank_account.md) | Bank account number for payments |
| [base_uom](base_uom.md) | Base unit of measure (each, kg, litre) |
| [carrier_eta](carrier_eta.md) | Carrier-estimated arrival date |
| [carrier_id](carrier_id.md) |  |
| [carrier_name](carrier_name.md) |  |
| [carrier_type](carrier_type.md) | OCEAN, AIR, ROAD, RAIL, PARCEL |
| [category](category.md) | Top-level category |
| [chargeable_weight_kg](chargeable_weight_kg.md) |  |
| [committed_date](committed_date.md) | Date committed to the customer |
| [confirmed_date](confirmed_date.md) | Supplier-confirmed delivery date (may differ from promised) |
| [contact_email](contact_email.md) | Primary contact email |
| [contact_name](contact_name.md) | Primary contact name |
| [country_code](country_code.md) | ISO 3166-1 alpha-2 country code of the supplier site |
| [currency](currency.md) | ISO 4217 currency code |
| [customer_id](customer_id.md) | Golden key for the customer |
| [customer_name](customer_name.md) |  |
| [deliver_to_plant_id](deliver_to_plant_id.md) |  |
| [description](description.md) |  |
| [destination_id](destination_id.md) | Customer ship-to or inter-plant destination |
| [destination_region](destination_region.md) |  |
| [duty_rate](duty_rate.md) | Ad valorem duty rate as a decimal (0 |
| [effective_from](effective_from.md) |  |
| [effective_to](effective_to.md) |  |
| [event_id](event_id.md) |  |
| [event_time_utc](event_time_utc.md) | Event timestamp in UTC |
| [event_type](event_type.md) | picked_up, departed, arrived, delivered, exception |
| [freight_charge](freight_charge.md) |  |
| [freight_currency](freight_currency.md) |  |
| [from_currency](from_currency.md) | ISO 4217 source currency |
| [fulfilled_from_location_id](fulfilled_from_location_id.md) |  |
| [fx_date](fx_date.md) |  |
| [hts_code](hts_code.md) | Harmonized Tariff Schedule code (6 or 10 digit) |
| [in_transit_qty](in_transit_qty.md) |  |
| [incoterm](incoterm.md) | Incoterms 2020 rule (EXW, FOB, CIF, DDP) |
| [is_first_shipment](is_first_shipment.md) | True if this is the first shipment against the sales order line |
| [lane_id](lane_id.md) |  |
| [line_number](line_number.md) |  |
| [location_id](location_id.md) | Identifier of the event location |
| [location_type](location_type.md) | RACK, BULK, COLD, YARD |
| [mode](mode.md) | Primary transport mode |
| [on_hand_qty](on_hand_qty.md) | Quantity on hand in base UOM |
| [on_hand_value_std](on_hand_value_std.md) | On-hand value in standard cost (USD) |
| [order_date](order_date.md) |  |
| [ordered_qty](ordered_qty.md) |  |
| [origin_plant_id](origin_plant_id.md) |  |
| [origin_region](origin_region.md) |  |
| [pack_factor](pack_factor.md) | Units per case |
| [pallet_factor](pallet_factor.md) | Cases per pallet |
| [parent_supplier_id](parent_supplier_id.md) | Parent supplier in the supplier hierarchy (site > parent) |
| [part_family](part_family.md) | Product family in the Part > ProductFamily > Category hierarchy |
| [part_id](part_id.md) | Golden key for the part |
| [part_name](part_name.md) |  |
| [plant_id](plant_id.md) |  |
| [plant_name](plant_name.md) |  |
| [plant_type](plant_type.md) | MANUFACTURING or DISTRIBUTION |
| [po_line_id](po_line_id.md) |  |
| [po_number](po_number.md) |  |
| [promised_date](promised_date.md) | Supplier-promised delivery date |
| [quality_status](quality_status.md) | ACCEPTED, REJECTED, QUARANTINE |
| [quoted_lead_days](quoted_lead_days.md) | Supplier-quoted lead time in calendar days |
| [rate](rate.md) | Units of to_currency per unit of from_currency |
| [receipt_date](receipt_date.md) |  |
| [receipt_id](receipt_id.md) |  |
| [received_qty](received_qty.md) |  |
| [region](region.md) | Geographic region (US, EMEA, APAC) |
| [requested_date](requested_date.md) | Customer-requested delivery date |
| [scac_code](scac_code.md) | Standard Carrier Alpha Code |
| [segment](segment.md) | Market segment (Industrial, Retail, Government, Healthcare) |
| [ship_date](ship_date.md) |  |
| [ship_to_id](ship_to_id.md) | Ship-to location in the Customer hierarchy |
| [shipment_id](shipment_id.md) |  |
| [shipment_line_id](shipment_line_id.md) |  |
| [shipped_qty](shipped_qty.md) |  |
| [site_tz](site_tz.md) | IANA timezone of the event location |
| [snapshot_date](snapshot_date.md) |  |
| [so_line_id](so_line_id.md) |  |
| [so_number](so_number.md) |  |
| [sold_to_id](sold_to_id.md) | Sold-to party |
| [source_systems](source_systems.md) | Systems of record (erp, portal) |
| [status](status.md) | OPEN, RECEIVED, PARTIAL, CANCELLED |
| [storage_location_id](storage_location_id.md) |  |
| [storage_location_name](storage_location_name.md) |  |
| [supplier_id](supplier_id.md) | Golden key for the supplier, resolved from crosswalk |
| [supplier_name](supplier_name.md) | Legal name of the supplier entity |
| [supplier_site](supplier_site.md) | Physical site identifier within the supplier organisation |
| [synonyms](synonyms.md) | Alternative names (vendor, seller) |
| [tariff_id](tariff_id.md) |  |
| [timezone](timezone.md) | IANA timezone identifier (e |
| [to_currency](to_currency.md) | Always USD |
| [transit_days_typical](transit_days_typical.md) |  |
| [unit_cost](unit_cost.md) | Agreed unit cost in the transaction currency |
| [unit_price](unit_price.md) |  |
| [weight_kg](weight_kg.md) | Unit weight in kilograms |


## Enumerations

| Enumeration | Description |
| --- | --- |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |
