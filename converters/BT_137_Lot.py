# converters/BT_137_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cbc:ID"
    lot_ids = root.xpath(xpath, namespaces=namespaces)
    
    if lot_ids:
        return {
            "tender": {
                "lots": [{"id": lot_id.text} for lot_id in lot_ids]
            }
        }
    else:
        logger.info("No lot identifiers found")
        return None

def merge_lot_identifier(release_json, lot_data):
    if not lot_data:
        logger.warning("No lot identifier data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])
    
    for new_lot in lot_data["tender"]["lots"]:
        if not any(lot["id"] == new_lot["id"] for lot in existing_lots):
            existing_lots.append(new_lot)
            logger.info(f"Added new lot with id: {new_lot['id']}")
        else:
            logger.info(f"Lot with id: {new_lot['id']} already exists, skipping")