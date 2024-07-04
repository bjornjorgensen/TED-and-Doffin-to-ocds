# converters/BT_21_Title.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_title(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    # BT-21-Lot
    lot_titles = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    if lot_titles:
        result["tender"]["lots"] = []
        for lot in lot_titles:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            lot_title = lot.xpath("cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
            lot_data = {"id": lot_id}
            if lot_title:
                lot_data["title"] = lot_title[0]
            result["tender"]["lots"].append(lot_data)

    # BT-21-LotsGroup
    lots_group_titles = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    if lots_group_titles:
        result["tender"]["lotGroups"] = []
        for group in lots_group_titles:
            group_id = group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            group_title = group.xpath("cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
            group_data = {"id": group_id}
            if group_title:
                group_data["title"] = group_title[0]
            result["tender"]["lotGroups"].append(group_data)

    # BT-21-Part and BT-21-Procedure
    part_title = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
    procedure_title = root.xpath("//cac:ProcurementProject/cbc:Name/text()", namespaces=namespaces)
    
    if part_title:
        result["tender"]["title"] = part_title[0]
    elif procedure_title:
        result["tender"]["title"] = procedure_title[0]

    return result if result["tender"] else None

def merge_title(release_json, title_data):
    if not title_data:
        logger.warning("No Title data to merge")
        return

    tender = release_json.setdefault("tender", {})
    
    if "lots" in title_data["tender"]:
        existing_lots = {lot["id"]: lot for lot in tender.get("lots", [])}
        for new_lot in title_data["tender"]["lots"]:
            if new_lot["id"] in existing_lots:
                existing_lots[new_lot["id"]].update(new_lot)
            else:
                existing_lots[new_lot["id"]] = new_lot
        tender["lots"] = list(existing_lots.values())
        logger.info(f"Merged Title data for {len(title_data['tender']['lots'])} lots")
    
    if "lotGroups" in title_data["tender"]:
        existing_groups = {group["id"]: group for group in tender.get("lotGroups", [])}
        for new_group in title_data["tender"]["lotGroups"]:
            if new_group["id"] in existing_groups:
                existing_groups[new_group["id"]].update(new_group)
            else:
                existing_groups[new_group["id"]] = new_group
        tender["lotGroups"] = list(existing_groups.values())
        logger.info(f"Merged Title data for {len(title_data['tender']['lotGroups'])} lot groups")
    
    if "title" in title_data["tender"]:
        tender["title"] = title_data["tender"]["title"]
        logger.info("Merged Title data for tender")