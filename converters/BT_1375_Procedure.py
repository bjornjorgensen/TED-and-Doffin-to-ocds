# converters/BT_1375_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_group_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lotGroups": []}}

    lots_groups = root.xpath("//cac:TenderingTerms/cac:LotDistribution/cac:LotsGroup", namespaces=namespaces)
    
    for group in lots_groups:
        group_id = group.xpath("cbc:LotsGroupID/text()", namespaces=namespaces)[0]
        lot_ids = group.xpath("cac:ProcurementProjectLotReference/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if group_id and lot_ids:
            lot_group = {
                "id": group_id,
                "relatedLots": lot_ids
            }
            result["tender"]["lotGroups"].append(lot_group)

    return result if result["tender"]["lotGroups"] else None

def merge_group_lot_identifier(release_json, group_lot_data):
    if not group_lot_data:
        logger.warning("No Group Lot Identifier data to merge")
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
    
    for new_group in group_lot_data["tender"]["lotGroups"]:
        existing_group = next((group for group in existing_lot_groups if group["id"] == new_group["id"]), None)
        if existing_group:
            existing_related_lots = set(existing_group.get("relatedLots", []))
            existing_related_lots.update(new_group["relatedLots"])
            existing_group["relatedLots"] = list(existing_related_lots)
        else:
            existing_lot_groups.append(new_group)

    logger.info(f"Merged Group Lot Identifier data for {len(group_lot_data['tender']['lotGroups'])} lot groups")