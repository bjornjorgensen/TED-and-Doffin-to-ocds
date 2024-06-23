# converters/BT_5131.py
from lxml import etree

def parse_place_performance_city(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"tender": {"items": [], "deliveryAddresses": []}}

    # Parse Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        realized_locations = lot_element.xpath("cac:ProcurementProject/cac:RealizedLocation/cac:Address", namespaces=namespaces)
        
        if realized_locations:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "relatedLot": lot_id,
                "deliveryAddresses": []
            }
            for location in realized_locations:
                city_name = location.xpath("cbc:CityName/text()", namespaces=namespaces)
                if city_name:
                    item["deliveryAddresses"].append({"locality": city_name[0]})
            if item["deliveryAddresses"]:
                result["tender"]["items"].append(item)

    # Parse Part
    part_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:RealizedLocation/cac:Address", namespaces=namespaces)
    for part_element in part_elements:
        city_name = part_element.xpath("cbc:CityName/text()", namespaces=namespaces)
        if city_name:
            result["tender"]["deliveryAddresses"].append({"locality": city_name[0]})

    # Parse Procedure
    procedure_elements = root.xpath("/*/cac:ProcurementProject/cac:RealizedLocation/cac:Address", namespaces=namespaces)
    for procedure_element in procedure_elements:
        city_name = procedure_element.xpath("cbc:CityName/text()", namespaces=namespaces)
        if city_name:
            result["tender"]["deliveryAddresses"].append({"locality": city_name[0]})

    return result if (result["tender"]["items"] or result["tender"]["deliveryAddresses"]) else None

def merge_place_performance_city(release_json, place_performance_city_data):
    if place_performance_city_data and "tender" in place_performance_city_data:
        tender = release_json.setdefault("tender", {})
        
        # Merge items (Lots)
        if "items" in place_performance_city_data["tender"]:
            existing_items = tender.setdefault("items", [])
            for new_item in place_performance_city_data["tender"]["items"]:
                existing_item = next((item for item in existing_items if item["relatedLot"] == new_item["relatedLot"]), None)
                if existing_item:
                    existing_item.setdefault("deliveryAddresses", []).extend(new_item["deliveryAddresses"])
                else:
                    existing_items.append(new_item)
        
        # Merge deliveryAddresses (Part and Procedure)
        if "deliveryAddresses" in place_performance_city_data["tender"]:
            existing_addresses = tender.setdefault("deliveryAddresses", [])
            for new_address in place_performance_city_data["tender"]["deliveryAddresses"]:
                if new_address not in existing_addresses:
                    existing_addresses.append(new_address)
