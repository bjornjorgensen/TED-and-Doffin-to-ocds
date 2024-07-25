# converters/BT_5071_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_place_performance_country_subdivision(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"items": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        realized_locations = lot.xpath("cac:ProcurementProject/cac:RealizedLocation", namespaces=namespaces)
        
        for index, location in enumerate(realized_locations):
            country_subdivision = location.xpath("cac:Address/cbc:CountrySubentityCode/text()", namespaces=namespaces)
            
            if country_subdivision:
                item = {
                    "id": str(index + 1),
                    "deliveryAddresses": [{"region": country_subdivision[0]}],
                    "relatedLot": lot_id
                }
                result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None

def merge_lot_place_performance_country_subdivision(release_json, lot_data):
    if not lot_data:
        logger.warning("No Lot Place Performance Country Subdivision data to merge")
        return

    tender_items = release_json.setdefault("tender", {}).setdefault("items", [])
    
    for new_item in lot_data["tender"]["items"]:
        existing_item = next((item for item in tender_items if item["id"] == new_item["id"] and item["relatedLot"] == new_item["relatedLot"]), None)
        
        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            for new_address in new_item["deliveryAddresses"]:
                existing_address = next((addr for addr in existing_addresses if "region" not in addr), None)
                if existing_address:
                    existing_address["region"] = new_address["region"]
                else:
                    existing_addresses.append(new_address)
        else:
            tender_items.append(new_item)

    logger.info(f"Merged Lot Place Performance Country Subdivision data for {len(lot_data['tender']['items'])} items")