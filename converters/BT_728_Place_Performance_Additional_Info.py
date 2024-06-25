# converters/BT_728_Place_Performance_Additional_Info.py
from lxml import etree

def parse_place_performance_additional_info(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {
        'lots': {},
        'part': [],
        'procedure': []
    }

    # Process Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        descriptions = lot.xpath("cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()", namespaces=namespaces)
        if descriptions:
            result['lots'][lot_id] = descriptions

    # Process Part
    part_descriptions = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()", namespaces=namespaces)
    result['part'] = part_descriptions

    # Process Procedure
    procedure_descriptions = root.xpath("//cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()", namespaces=namespaces)
    result['procedure'] = procedure_descriptions

    return result

def merge_place_performance_additional_info(release_json, performance_data):
    tender = release_json.setdefault("tender", {})

    # Merge Lots
    items = tender.setdefault("items", [])
    for lot_id, descriptions in performance_data['lots'].items():
        item = next((item for item in items if item.get("relatedLot") == lot_id), None)
        if not item:
            item = {"id": str(len(items) + 1), "relatedLot": lot_id}
            items.append(item)
        if descriptions:
            delivery_locations = item.setdefault("deliveryLocations", [])
            existing_location = next((loc for loc in delivery_locations if "description" in loc), None)
            if existing_location:
                existing_location["description"] += f", {', '.join(descriptions)}"
            else:
                delivery_locations.append({"description": ', '.join(descriptions)})

    # Merge Part and Procedure
    all_descriptions = performance_data['part'] + performance_data['procedure']
    if all_descriptions:
        delivery_addresses = tender.setdefault("deliveryAddresses", [])
        existing_address = next((addr for addr in delivery_addresses if "description" in addr), None)
        if existing_address:
            existing_address["description"] += f", {', '.join(all_descriptions)}"
        else:
            delivery_addresses.append({"description": ', '.join(all_descriptions)})

    # Remove empty arrays
    for item in items:
        if "deliveryLocations" in item and not item["deliveryLocations"]:
            del item["deliveryLocations"]
    if "deliveryAddresses" in tender and not tender["deliveryAddresses"]:
        del tender["deliveryAddresses"]

    return release_json