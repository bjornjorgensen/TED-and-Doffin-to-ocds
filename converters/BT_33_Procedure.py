# converters/BT_33_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_max_lots_awarded(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    max_lots_awarded = root.xpath("//cac:LotDistribution/cbc:MaximumLotsAwardedNumeric/text()", namespaces=namespaces)
    
    if max_lots_awarded:
        try:
            return {"tender": {"lotDetails": {"maximumLotsAwardedPerSupplier": int(max_lots_awarded[0])}}}
        except ValueError:
            logger.warning(f"Invalid MaximumLotsAwardedNumeric value: {max_lots_awarded[0]}")
    
    return None

def merge_max_lots_awarded(release_json, max_lots_awarded_data):
    if not max_lots_awarded_data:
        return

    release_json.setdefault("tender", {}).setdefault("lotDetails", {}).update(
        max_lots_awarded_data["tender"]["lotDetails"]
    )
    logger.info("Merged Maximum Lots Awarded data")