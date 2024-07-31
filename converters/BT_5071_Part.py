# converters/BT_5071_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_part_place_performance_country_subdivision(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"deliveryAddresses": []}}

    parts = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces)
    
    for part in parts:
        realized_locations = part.xpath("cac:ProcurementProject/cac:RealizedLocation", namespaces=namespaces)
        
        for location in realized_locations:
            country_subdivision = location.xpath("cac:Address/cbc:CountrySubentityCode/text()", namespaces=namespaces)
            
            if country_subdivision:
                address = {"region": country_subdivision[0]}
                if address not in result["tender"]["deliveryAddresses"]:
                    result["tender"]["deliveryAddresses"].append(address)

    return result if result["tender"]["deliveryAddresses"] else None

def merge_part_place_performance_country_subdivision(release_json, part_data):
    if not part_data:
        logger.warning("No Part Place Performance Country Subdivision data to merge")
        return

    tender_delivery_addresses = release_json.setdefault("tender", {}).setdefault("deliveryAddresses", [])
    
    for new_address in part_data["tender"]["deliveryAddresses"]:
        existing_address = next((addr for addr in tender_delivery_addresses if addr.get("region") == new_address["region"]), None)
        if existing_address:
            # Address with this region already exists, no need to update
            continue
        else:
            tender_delivery_addresses.append(new_address)

    logger.info(f"Merged Part Place Performance Country Subdivision data for {len(part_data['tender']['deliveryAddresses'])} addresses")