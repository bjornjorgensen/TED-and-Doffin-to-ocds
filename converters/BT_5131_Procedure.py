# converters/BT_5131_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_place_performance_city_procedure(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"deliveryAddresses": []}}

    cities = root.xpath("//cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CityName/text()", namespaces=namespaces)
    
    for city in cities:
        result["tender"]["deliveryAddresses"].append({"locality": city})

    return result if result["tender"]["deliveryAddresses"] else None

def merge_place_performance_city_procedure(release_json, place_performance_city_procedure_data):
    if not place_performance_city_procedure_data:
        logger.warning("No Place Performance City Procedure data to merge")
        return

    tender_delivery_addresses = release_json.setdefault("tender", {}).setdefault("deliveryAddresses", [])

    for new_address in place_performance_city_procedure_data["tender"]["deliveryAddresses"]:
        matching_address = next((addr for addr in tender_delivery_addresses if addr.get("locality") == new_address["locality"]), None)
        if matching_address:
            matching_address.update(new_address)
        else:
            tender_delivery_addresses.append(new_address)

    logger.info(f"Merged Place Performance City Procedure data for {len(place_performance_city_procedure_data['tender']['deliveryAddresses'])} addresses")