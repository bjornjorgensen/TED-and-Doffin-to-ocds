# converters/BT_5101a_Part.py

from lxml import etree

def parse_part_place_performance_street(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"deliveryAddresses": []}}

    parts = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    
    for part in parts:
        realized_locations = part.xpath("cac:ProcurementProject/cac:RealizedLocation", namespaces=namespaces)
        
        for location in realized_locations:
            address = location.xpath("cac:Address", namespaces=namespaces)[0]
            street_name = address.xpath("cbc:StreetName/text()", namespaces=namespaces)
            additional_street_name = address.xpath("cbc:AdditionalStreetName/text()", namespaces=namespaces)
            address_lines = address.xpath("cac:AddressLine/cbc:Line/text()", namespaces=namespaces)
            
            street_address_parts = []
            if street_name:
                street_address_parts.append(street_name[0])
            if additional_street_name:
                street_address_parts.append(additional_street_name[0])
            street_address_parts.extend(address_lines)
            
            street_address = ", ".join(street_address_parts)
            
            result["tender"]["deliveryAddresses"].append({"streetAddress": street_address})

    return result if result["tender"]["deliveryAddresses"] else None

def merge_part_place_performance_street(release_json, part_place_performance_street_data):
    if not part_place_performance_street_data:
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault("deliveryAddresses", [])
    
    for new_address in part_place_performance_street_data["tender"]["deliveryAddresses"]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)