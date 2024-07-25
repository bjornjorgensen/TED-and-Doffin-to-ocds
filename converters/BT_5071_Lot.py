# converters/BT_5071_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_place_performance_country_subdivision(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"items": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        realized_locations = lot.xpath(".//cac:RealizedLocation", namespaces=namespaces)
        
        for index, location in enumerate(realized_locations):
            country_subdivision = location.xpath(".//cbc:CountrySubentityCode[@listName='nuts=lvl3']/text()", namespaces=namespaces)
            
            if country_subdivision:
                item = {
                    "id": str(index + 1),
                    "deliveryAddresses": [{"region": country_subdivision[0]}],
                    "relatedLot": lot_id
                }
                result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None

def merge_place_performance_country_subdivision(release_json, subdivision_data):
    if not subdivision_data:
        logger.warning("No Place Performance Country Subdivision data to merge")
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])
    
    for new_item in subdivision_data["tender"]["items"]:
        existing_item = next((item for item in existing_items if item["relatedLot"] == new_item["relatedLot"]), None)
        
        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            if existing_addresses:
                existing_addresses[0].update(new_item["deliveryAddresses"][0])
            else:
                existing_addresses.extend(new_item["deliveryAddresses"])
        else:
            existing_items.append(new_item)

    logger.info(f"Merged Place Performance Country Subdivision data for {len(subdivision_data['tender']['items'])} items")