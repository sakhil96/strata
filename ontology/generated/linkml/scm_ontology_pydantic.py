from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.11.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'https://scm-ontology.example.com/schema/',
     'default_range': 'string',
     'description': 'An enterprise supply chain ontology covering procurement, '
                    'logistics, inventory and sales order fulfilment. Entities map '
                    'to the IOF Supply Chain Reference Ontology where a class '
                    'exists.',
     'id': 'https://scm-ontology.example.com/schema',
     'imports': ['linkml:types'],
     'name': 'scm_ontology',
     'prefixes': {'iof_scro': {'prefix_prefix': 'iof_scro',
                               'prefix_reference': 'https://spec.industrialontologies.org/ontology/supplychain/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'scm': {'prefix_prefix': 'scm',
                          'prefix_reference': 'https://scm-ontology.example.com/schema/'}},
     'source_file': '/Users/apple/supplyC/ontology/ontology.yaml',
     'title': 'Supply Chain Ontology'} )


class Supplier(ConfiguredBaseModel):
    """
    An organisation that supplies parts under contractual agreements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:Supplier',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    supplier_id: str = Field(default=..., description="""Golden key for the supplier, resolved from crosswalk.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'SupplierPartAgreement', 'PurchaseOrderLine']} })
    supplier_name: Optional[str] = Field(default=None, description="""Legal name of the supplier entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier']} })
    supplier_site: Optional[str] = Field(default=None, description="""Physical site identifier within the supplier organisation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier']} })
    parent_supplier_id: Optional[str] = Field(default=None, description="""Parent supplier in the supplier hierarchy (site > parent).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier']} })
    country_code: Optional[str] = Field(default=None, description="""ISO 3166-1 alpha-2 country code of the supplier site.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'Plant', 'Customer']} })
    contact_name: Optional[str] = Field(default=None, description="""Primary contact name.""", json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity',
                                         'value': 'CONFIDENTIAL'}},
         'domain_of': ['Supplier', 'Customer']} })
    contact_email: Optional[str] = Field(default=None, description="""Primary contact email.""", json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity',
                                         'value': 'CONFIDENTIAL'}},
         'domain_of': ['Supplier', 'Customer']} })
    bank_account: Optional[str] = Field(default=None, description="""Bank account number for payments.""", json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity', 'value': 'RESTRICTED'}},
         'domain_of': ['Supplier']} })
    source_systems: Optional[list[str]] = Field(default=None, description="""Systems of record (erp, portal).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'Part']} })
    synonyms: Optional[list[str]] = Field(default=None, description="""Alternative names (vendor, seller).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier']} })


class Part(ConfiguredBaseModel):
    """
    A stock-keeping unit that can be purchased, stored, and sold.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:MaterialProduct',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    part_id: str = Field(default=..., description="""Golden key for the part.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part',
                       'SupplierPartAgreement',
                       'PurchaseOrderLine',
                       'SalesOrderLine',
                       'InventorySnapshot',
                       'TariffCode']} })
    part_name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Part']} })
    part_family: Optional[str] = Field(default=None, description="""Product family in the Part > ProductFamily > Category hierarchy.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part']} })
    category: Optional[str] = Field(default=None, description="""Top-level category.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part']} })
    base_uom: Optional[str] = Field(default=None, description="""Base unit of measure (each, kg, litre).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part']} })
    pack_factor: Optional[float] = Field(default=None, description="""Units per case.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part']} })
    pallet_factor: Optional[float] = Field(default=None, description="""Cases per pallet.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part']} })
    weight_kg: Optional[float] = Field(default=None, description="""Unit weight in kilograms.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part']} })
    source_systems: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'Part']} })


class SupplierPartAgreement(ConfiguredBaseModel):
    """
    A contractual agreement for a supplier to supply a specific part.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:SupplyAgreement',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    agreement_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement']} })
    supplier_id: Optional[str] = Field(default=None, description="""The supplying party.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'SupplierPartAgreement', 'PurchaseOrderLine']} })
    part_id: Optional[str] = Field(default=None, description="""The supplied part.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part',
                       'SupplierPartAgreement',
                       'PurchaseOrderLine',
                       'SalesOrderLine',
                       'InventorySnapshot',
                       'TariffCode']} })
    unit_cost: Optional[float] = Field(default=None, description="""Agreed unit cost in the transaction currency.""", json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity', 'value': 'RESTRICTED'}},
         'domain_of': ['SupplierPartAgreement', 'PurchaseOrderLine']} })
    currency: Optional[str] = Field(default=None, description="""ISO 4217 currency code.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement', 'PurchaseOrderLine', 'SalesOrderLine']} })
    incoterm: Optional[str] = Field(default=None, description="""Incoterms 2020 rule (EXW, FOB, CIF, DDP).""", json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement']} })
    quoted_lead_days: Optional[int] = Field(default=None, description="""Supplier-quoted lead time in calendar days.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement']} })
    effective_from: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement', 'TariffCode']} })
    effective_to: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement', 'TariffCode']} })


class Plant(ConfiguredBaseModel):
    """
    A manufacturing or distribution facility.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:Facility',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    plant_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Plant', 'StorageLocation']} })
    plant_name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Plant']} })
    plant_type: Optional[str] = Field(default=None, description="""MANUFACTURING or DISTRIBUTION.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Plant']} })
    region: Optional[str] = Field(default=None, description="""Geographic region (US, EMEA, APAC).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Plant']} })
    country_code: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'Plant', 'Customer']} })
    timezone: Optional[str] = Field(default=None, description="""IANA timezone identifier (e.g. America/Chicago).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Plant']} })


class StorageLocation(ConfiguredBaseModel):
    """
    A named location within a plant where inventory is held.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:StorageLocation',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    storage_location_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation', 'InventorySnapshot']} })
    storage_location_name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation']} })
    plant_id: Optional[str] = Field(default=None, description="""The containing plant.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Plant', 'StorageLocation']} })
    location_type: Optional[str] = Field(default=None, description="""RACK, BULK, COLD, YARD.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation']} })


class Customer(ConfiguredBaseModel):
    """
    An organisation that purchases finished goods.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:Customer',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    customer_id: str = Field(default=..., description="""Golden key for the customer.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Customer', 'SalesOrderLine']} })
    customer_name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Customer']} })
    ship_to_id: Optional[str] = Field(default=None, description="""Ship-to location in the Customer hierarchy.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Customer']} })
    sold_to_id: Optional[str] = Field(default=None, description="""Sold-to party.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Customer']} })
    account_id: Optional[str] = Field(default=None, description="""Account in the hierarchy.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Customer']} })
    segment: Optional[str] = Field(default=None, description="""Market segment (Industrial, Retail, Government, Healthcare).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Customer']} })
    country_code: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'Plant', 'Customer']} })
    contact_name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity',
                                         'value': 'CONFIDENTIAL'}},
         'domain_of': ['Supplier', 'Customer']} })
    contact_email: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity',
                                         'value': 'CONFIDENTIAL'}},
         'domain_of': ['Supplier', 'Customer']} })


class PurchaseOrderLine(ConfiguredBaseModel):
    """
    A line on a purchase order placed with a supplier.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:PurchaseOrderLine',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    po_line_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'GoodsReceipt']} })
    po_number: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine']} })
    line_number: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'SalesOrderLine']} })
    supplier_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Supplier', 'SupplierPartAgreement', 'PurchaseOrderLine']} })
    part_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Part',
                       'SupplierPartAgreement',
                       'PurchaseOrderLine',
                       'SalesOrderLine',
                       'InventorySnapshot',
                       'TariffCode']} })
    deliver_to_plant_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine']} })
    ordered_qty: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'SalesOrderLine']} })
    unit_cost: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity', 'value': 'RESTRICTED'}},
         'domain_of': ['SupplierPartAgreement', 'PurchaseOrderLine']} })
    currency: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement', 'PurchaseOrderLine', 'SalesOrderLine']} })
    order_date: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine']} })
    promised_date: Optional[date] = Field(default=None, description="""Supplier-promised delivery date.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine']} })
    confirmed_date: Optional[date] = Field(default=None, description="""Supplier-confirmed delivery date (may differ from promised).""", json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine']} })
    status: Optional[str] = Field(default=None, description="""OPEN, RECEIVED, PARTIAL, CANCELLED.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'SalesOrderLine', 'Shipment']} })


class GoodsReceipt(ConfiguredBaseModel):
    """
    A record of parts received against a purchase order line.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:GoodsReceipt',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    receipt_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['GoodsReceipt']} })
    po_line_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'GoodsReceipt']} })
    receipt_date: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['GoodsReceipt']} })
    received_qty: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['GoodsReceipt']} })
    quality_status: Optional[str] = Field(default=None, description="""ACCEPTED, REJECTED, QUARANTINE.""", json_schema_extra = { "linkml_meta": {'domain_of': ['GoodsReceipt']} })


class SalesOrderLine(ConfiguredBaseModel):
    """
    A line on a customer sales order.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:SalesOrderLine',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    so_line_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine', 'ShipmentLine']} })
    so_number: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine']} })
    line_number: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'SalesOrderLine']} })
    customer_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Customer', 'SalesOrderLine']} })
    part_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Part',
                       'SupplierPartAgreement',
                       'PurchaseOrderLine',
                       'SalesOrderLine',
                       'InventorySnapshot',
                       'TariffCode']} })
    fulfilled_from_location_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine']} })
    ordered_qty: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'SalesOrderLine']} })
    unit_price: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine']} })
    currency: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement', 'PurchaseOrderLine', 'SalesOrderLine']} })
    requested_date: Optional[date] = Field(default=None, description="""Customer-requested delivery date.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine']} })
    committed_date: Optional[date] = Field(default=None, description="""Date committed to the customer.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine']} })
    actual_ship_date: Optional[date] = Field(default=None, description="""Date the shipment left the warehouse.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine']} })
    actual_delivery_date: Optional[date] = Field(default=None, description="""Date confirmed delivered to the customer.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine']} })
    status: Optional[str] = Field(default=None, description="""OPEN, SHIPPED, DELIVERED, CANCELLED.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'SalesOrderLine', 'Shipment']} })


class Shipment(ConfiguredBaseModel):
    """
    A transport movement from origin to destination.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:Shipment',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    shipment_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment', 'ShipmentLine', 'DeliveryEvent']} })
    carrier_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment', 'Carrier']} })
    lane_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment', 'Lane']} })
    origin_plant_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment']} })
    destination_id: Optional[str] = Field(default=None, description="""Customer ship-to or inter-plant destination.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment']} })
    ship_date: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment']} })
    carrier_eta: Optional[date] = Field(default=None, description="""Carrier-estimated arrival date.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment']} })
    actual_delivery: Optional[date] = Field(default=None, description="""Actual delivery date from carrier confirmation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment']} })
    chargeable_weight_kg: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment']} })
    freight_charge: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'annotations': {'sensitivity': {'tag': 'sensitivity', 'value': 'RESTRICTED'}},
         'domain_of': ['Shipment']} })
    freight_currency: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment']} })
    status: Optional[str] = Field(default=None, description="""IN_TRANSIT, DELIVERED, EXCEPTION.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PurchaseOrderLine', 'SalesOrderLine', 'Shipment']} })


class ShipmentLine(ConfiguredBaseModel):
    """
    Links a sales order line to a shipment with the shipped quantity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://scm-ontology.example.com/schema'})

    shipment_line_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['ShipmentLine']} })
    shipment_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment', 'ShipmentLine', 'DeliveryEvent']} })
    so_line_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SalesOrderLine', 'ShipmentLine']} })
    shipped_qty: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['ShipmentLine']} })
    is_first_shipment: Optional[bool] = Field(default=None, description="""True if this is the first shipment against the sales order line.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ShipmentLine']} })


class Carrier(ConfiguredBaseModel):
    """
    A freight carrier or logistics service provider.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:Carrier',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    carrier_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment', 'Carrier']} })
    carrier_name: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Carrier']} })
    carrier_type: Optional[str] = Field(default=None, description="""OCEAN, AIR, ROAD, RAIL, PARCEL.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Carrier']} })
    scac_code: Optional[str] = Field(default=None, description="""Standard Carrier Alpha Code.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Carrier']} })


class Lane(ConfiguredBaseModel):
    """
    A defined transportation route between an origin and destination.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://scm-ontology.example.com/schema'})

    lane_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment', 'Lane']} })
    origin_region: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Lane']} })
    destination_region: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Lane']} })
    mode: Optional[str] = Field(default=None, description="""Primary transport mode.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Lane']} })
    transit_days_typical: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Lane']} })


class DeliveryEvent(ConfiguredBaseModel):
    """
    A timestamped event in the lifecycle of a shipment.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://scm-ontology.example.com/schema'})

    event_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['DeliveryEvent']} })
    shipment_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Shipment', 'ShipmentLine', 'DeliveryEvent']} })
    event_type: Optional[str] = Field(default=None, description="""picked_up, departed, arrived, delivered, exception.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DeliveryEvent']} })
    event_time_utc: Optional[datetime ] = Field(default=None, description="""Event timestamp in UTC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DeliveryEvent']} })
    site_tz: Optional[str] = Field(default=None, description="""IANA timezone of the event location.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DeliveryEvent']} })
    location_id: Optional[str] = Field(default=None, description="""Identifier of the event location.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DeliveryEvent']} })


class InventorySnapshot(ConfiguredBaseModel):
    """
    A daily snapshot of inventory at a storage location for a part.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'iof_scro:InventoryPosition',
         'from_schema': 'https://scm-ontology.example.com/schema'})

    storage_location_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['StorageLocation', 'InventorySnapshot']} })
    part_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Part',
                       'SupplierPartAgreement',
                       'PurchaseOrderLine',
                       'SalesOrderLine',
                       'InventorySnapshot',
                       'TariffCode']} })
    snapshot_date: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['InventorySnapshot']} })
    on_hand_qty: Optional[float] = Field(default=None, description="""Quantity on hand in base UOM.""", json_schema_extra = { "linkml_meta": {'domain_of': ['InventorySnapshot']} })
    on_hand_value_std: Optional[float] = Field(default=None, description="""On-hand value in standard cost (USD).""", json_schema_extra = { "linkml_meta": {'domain_of': ['InventorySnapshot']} })
    in_transit_qty: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['InventorySnapshot']} })
    allocated_qty: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['InventorySnapshot']} })


class TariffCode(ConfiguredBaseModel):
    """
    An HTS tariff classification with duty rates and effective dates.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://scm-ontology.example.com/schema'})

    tariff_id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['TariffCode']} })
    hts_code: Optional[str] = Field(default=None, description="""Harmonized Tariff Schedule code (6 or 10 digit).""", json_schema_extra = { "linkml_meta": {'domain_of': ['TariffCode']} })
    description: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TariffCode']} })
    duty_rate: Optional[float] = Field(default=None, description="""Ad valorem duty rate as a decimal (0.05 = 5%).""", json_schema_extra = { "linkml_meta": {'domain_of': ['TariffCode']} })
    effective_from: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement', 'TariffCode']} })
    effective_to: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['SupplierPartAgreement', 'TariffCode']} })
    part_id: Optional[str] = Field(default=None, description="""The part classified under this tariff code.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Part',
                       'SupplierPartAgreement',
                       'PurchaseOrderLine',
                       'SalesOrderLine',
                       'InventorySnapshot',
                       'TariffCode']} })


class FxRate(ConfiguredBaseModel):
    """
    A daily foreign exchange rate to USD; keyed by date and source currency.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://scm-ontology.example.com/schema'})

    fx_date: Optional[date] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['FxRate']} })
    from_currency: Optional[str] = Field(default=None, description="""ISO 4217 source currency.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FxRate']} })
    to_currency: Optional[str] = Field(default=None, description="""Always USD.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FxRate']} })
    rate: Optional[float] = Field(default=None, description="""Units of to_currency per unit of from_currency.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FxRate']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Supplier.model_rebuild()
Part.model_rebuild()
SupplierPartAgreement.model_rebuild()
Plant.model_rebuild()
StorageLocation.model_rebuild()
Customer.model_rebuild()
PurchaseOrderLine.model_rebuild()
GoodsReceipt.model_rebuild()
SalesOrderLine.model_rebuild()
Shipment.model_rebuild()
ShipmentLine.model_rebuild()
Carrier.model_rebuild()
Lane.model_rebuild()
DeliveryEvent.model_rebuild()
InventorySnapshot.model_rebuild()
TariffCode.model_rebuild()
FxRate.model_rebuild()
