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
    lot_titles = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:ProcurementProject/cbc:Name", namespaces=namespaces)
    if lot_titles:
        result["tender"]["lots"] = []
        for lot_title in lot_titles:
            lot_id = lot_title.xpath("../../cbc:ID", namespaces=namespaces)[0].text
            result["tender"]["lots"].append({
                "id": lot_id,
                "title": lot_title.text
            })

    # BT-21-LotsGroup
    lots_group_titles = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:ProcurementProject/cbc:Name", namespaces=namespaces)
    if lots_group_titles:
        result["tender"]["lotGroups"] = []
        for group_title in lots_group_titles:
            group_id = group_title.xpath("../../cbc:ID", namespaces=namespaces)[0].text
            result["tender"]["lotGroups"].append({
                "id": group_id,
                "title": group_title.text
            })

    # BT-21-Part and BT-21-Procedure
    part_title = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Name", namespaces=namespaces)
    procedure_title = root.xpath("//cac:ProcurementProject/cbc:Name", namespaces=namespaces)
    
    if part_title:
        result["tender"]["title"] = part_title[0].text
    elif procedure_title:
        result["tender"]["title"] = procedure_title[0].text

    return result if result["tender"] else None

def merge_title(release_json, title_data):
    if not title_data:
        logger.warning("No Title data to merge")
        return

    tender = release_json.setdefault("tender", {})
    
    if "lots" in title_data["tender"]:
        tender.setdefault("lots", []).extend(title_data["tender"]["lots"])
        logger.info(f"Merged Title data for {len(title_data['tender']['lots'])} lots")
    
    if "lotGroups" in title_data["tender"]:
        tender.setdefault("lotGroups", []).extend(title_data["tender"]["lotGroups"])
        logger.info(f"Merged Title data for {len(title_data['tender']['lotGroups'])} lot groups")
    
    if "title" in title_data["tender"]:
        tender["title"] = title_data["tender"]["title"]
        logger.info("Merged Title data for tender")