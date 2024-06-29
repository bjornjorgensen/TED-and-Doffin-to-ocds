# converters/BT_1375_Procedure.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_group_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lotGroups": []}}
    lots_groups = root.xpath("//cac:TenderingTerms/cac:LotDistribution/cac:LotsGroup", namespaces=namespaces)

    for lots_group in lots_groups:
        group_id = lots_group.xpath("cbc:LotsGroupID[@schemeName='LotsGroup']/text()", namespaces=namespaces)
        lot_ids = lots_group.xpath("cac:ProcurementProjectLotReference/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)

        if group_id and lot_ids:
            lot_group = next((g for g in result["tender"]["lotGroups"] if g["id"] == group_id[0]), None)
            if not lot_group:
                lot_group = {"id": group_id[0], "relatedLots": []}
                result["tender"]["lotGroups"].append(lot_group)
            
            for lot_id in lot_ids:
                if lot_id not in lot_group["relatedLots"]:
                    lot_group["relatedLots"].append(lot_id)

    return result if result["tender"]["lotGroups"] else None

def merge_group_lot_identifier(release_json, group_lot_data):
    if not group_lot_data:
        logger.warning("No Group Lot Identifier data to merge")
        return

    existing_lot_groups = release_json.setdefault("tender", {}).setdefault("lotGroups", [])
    
    for new_group in group_lot_data["tender"]["lotGroups"]:
        existing_group = next((g for g in existing_lot_groups if g["id"] == new_group["id"]), None)
        if existing_group:
            existing_group.setdefault("relatedLots", []).extend(
                lot for lot in new_group["relatedLots"] if lot not in existing_group.get("relatedLots", [])
            )
        else:
            existing_lot_groups.append(new_group)

    logger.info(f"Merged Group Lot Identifier data for {len(group_lot_data['tender']['lotGroups'])} lot groups")