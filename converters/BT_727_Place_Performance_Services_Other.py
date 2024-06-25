# converters/BT_727_Place_Performance_Services_Other.py
from lxml import etree

REGION_MAPPING = {
    "anyw": "Anywhere",
    "anyw-cou": "Anywhere in the given country",
    "anyw-eea": "Anywhere in the European Economic Area"
}

def parse_place_performance_services_other(xml_content):
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
        regions = lot.xpath("cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:Region/text()", namespaces=namespaces)
        if regions:
            result['lots'][lot_id] = [REGION_MAPPING.get(region, region) for region in regions]

    # Process Part
    part_regions = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:Region/text()", namespaces=namespaces)
    result['part'] = [REGION_MAPPING.get(region, region) for region in part_regions]

    # Process Procedure
    procedure_regions = root.xpath("//cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:Region/text()", namespaces=namespaces)
    result['procedure'] = [REGION_MAPPING.get(region, region) for region in procedure_regions]

    return result

def merge_place_performance_services_other(release_json, performance_data):
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
        delivery_locations = tender.setdefault("deliveryLocations", [])
        existing_location = next((loc for loc in delivery_locations if "description" in loc), None)
        if existing_location:
            existing_location["description"] += f", {', '.join(all_descriptions)}"
        else:
            delivery_locations.append({"description": ', '.join(all_descriptions)})

    # Remove empty deliveryLocations arrays
    for item in items:
        if "deliveryLocations" in item and not item["deliveryLocations"]:
            del item["deliveryLocations"]
    if "deliveryLocations" in tender and not tender["deliveryLocations"]:
        del tender["deliveryLocations"]

    return release_json