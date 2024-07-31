# converters/BT_330_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_group_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    group_ids = root.xpath("//cac:LotDistribution/cac:LotsGroup/cbc:LotsGroupID/text()", namespaces=namespaces)
    
    if group_ids:
        return {"tender": {"lotGroups": [{"id": group_id} for group_id in group_ids]}}
    
    return None

def merge_group_identifier(release_json, group_identifier_data):
    if not group_identifier_data:
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
    
    for new_group in group_identifier_data["tender"]["lotGroups"]:
        if not any(existing_group["id"] == new_group["id"] for existing_group in existing_lot_groups):
            existing_lot_groups.append(new_group)
    
    logger.info(f"Merged {len(group_identifier_data['tender']['lotGroups'])} Group Identifier(s)")