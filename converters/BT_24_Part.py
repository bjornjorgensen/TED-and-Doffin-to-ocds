# converters/BT_24_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_part_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    description = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
    
    if description:
        result["tender"]["description"] = description[0]
        return result
    
    return None

def merge_part_description(release_json, part_description_data):
    if not part_description_data:
        logger.warning("No Part Description data to merge")
        return

    release_json.setdefault("tender", {})["description"] = part_description_data["tender"]["description"]
    logger.info("Merged Part Description data")