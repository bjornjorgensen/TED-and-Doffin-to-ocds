# converters/BT_137_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_part_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cbc:ID"
    part_ids = root.xpath(xpath, namespaces=namespaces)
    
    if part_ids:
        # We take the first 'Part' ID found, as tender.id should be a single value
        return {
            "tender": {
                "id": part_ids[0].text
            }
        }
    else:
        logger.info("No part identifier found")
        return None

def merge_part_identifier(release_json, part_data):
    if not part_data:
        logger.warning("No part identifier data to merge")
        return

    tender = release_json.setdefault("tender", {})
    if "id" in tender:
        logger.warning(f"Tender ID already exists. Overwriting with new value: {part_data['tender']['id']}")
    
    tender["id"] = part_data["tender"]["id"]
    logger.info(f"Set tender.id to: {tender['id']}")