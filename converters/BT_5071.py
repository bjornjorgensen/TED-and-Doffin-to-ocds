# converters/BT_5071.py
from lxml import etree

def parse_place_performance_country_subdivision(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {}}

    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    items = []
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        realized_locations = lot_element.xpath("cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode/text()", namespaces=namespaces)
        
        if realized_locations:
            item = {
                "id": str(len(items) + 1),
                "relatedLot": lot_id,
                "deliveryAddresses": [{"region": location} for location in realized_locations]
            }
            items.append(item)
    
    if items:
        result["tender"]["items"] = items

    # Parse Part and Procedure
    delivery_addresses = []
    part_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode", namespaces=namespaces)
    procedure_elements = root.xpath("/*/cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode", namespaces=namespaces)
    
    for element in part_elements + procedure_elements:
        delivery_addresses.append({"region": element.text})
    
    if delivery_addresses:
        result["tender"]["deliveryAddresses"] = delivery_addresses

    return result if result["tender"] else None

def merge_place_performance_country_subdivision(release_json, place_performance_data):
    if place_performance_data and "tender" in place_performance_data:
        tender = release_json.setdefault("tender", {})
        
        # Merge items (Lots)
        if "items" in place_performance_data["tender"]:
            existing_items = tender.setdefault("items", [])
            for new_item in place_performance_data["tender"]["items"]:
                existing_item = next((item for item in existing_items if item["relatedLot"] == new_item["relatedLot"]), None)
                if existing_item:
                    existing_item.setdefault("deliveryAddresses", []).extend(new_item["deliveryAddresses"])
                else:
                    existing_items.append(new_item)
        
        # Merge deliveryAddresses (Part and Procedure)
        if "deliveryAddresses" in place_performance_data["tender"]:
            existing_addresses = tender.setdefault("deliveryAddresses", [])
            for new_address in place_performance_data["tender"]["deliveryAddresses"]:
                if new_address not in existing_addresses:
                    existing_addresses.append(new_address)
