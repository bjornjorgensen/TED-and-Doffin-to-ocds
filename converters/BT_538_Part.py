# converters/BT_538_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_part_duration_other(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    duration_code = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:DescriptionCode[@listName='timeperiod']/text()", namespaces=namespaces)
    
    if duration_code:
        result["tender"]["contractPeriod"] = {
            "description": duration_code[0]
        }

    return result if result["tender"] else None

def merge_part_duration_other(release_json, part_duration_other_data):
    if not part_duration_other_data:
        logger.warning("No Part Duration Other data to merge")
        return

    tender = release_json.setdefault("tender", {})
    
    if "contractPeriod" in part_duration_other_data["tender"]:
        tender.setdefault("contractPeriod", {}).update(part_duration_other_data["tender"]["contractPeriod"])
        logger.info("Merged Part Duration Other data")
    else:
        logger.info("No Part Duration Other data to merge")