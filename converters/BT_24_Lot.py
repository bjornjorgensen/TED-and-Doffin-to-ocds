# converters/BT_24_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_description(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot_element.xpath("cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
        
        if description:
            lot = {
                "id": lot_id,
                "description": description[0]
            }
            result["tender"]["lots"].append(lot)

    return result if result["tender"]["lots"] else None

def merge_lot_description(release_json, lot_description_data):
    if not lot_description_data:
        logger.warning("No Lot Description data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in lot_description_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot["description"] = new_lot["description"]
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Lot Description data for {len(lot_description_data['tender']['lots'])} lots")