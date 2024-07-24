# converters/BT_54_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_options_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        options_description = lot.xpath("cac:ProcurementProject/cac:ContractExtension/cbc:OptionsDescription/text()", namespaces=namespaces)
        
        if options_description:
            lot_data = {
                "id": lot_id,
                "options": {
                    "description": options_description[0]
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_options_description(release_json, options_description_data):
    if not options_description_data:
        logger.warning("No Options Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in options_description_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("options", {}).update(new_lot["options"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged Options Description data for {len(options_description_data['tender']['lots'])} lots")