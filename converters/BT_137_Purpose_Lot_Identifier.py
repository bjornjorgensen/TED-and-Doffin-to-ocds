# converters/BT_137_Purpose_Lot_Identifier.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_purpose_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": [], "lotGroups": []}}

    # Process Lots
    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        result["tender"]["lots"].append({"id": lot_id})

    # Process Lots Groups
    lots_groups = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for group in lots_groups:
        group_id = group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        result["tender"]["lotGroups"].append({"id": group_id})

    # Process Part
    part = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cbc:ID/text()", namespaces=namespaces)
    if part:
        result["tender"]["id"] = part[0]

    return result if result["tender"]["lots"] or result["tender"]["lotGroups"] or "id" in result["tender"] else None

def merge_purpose_lot_identifier(release_json, purpose_lot_data):
    if not purpose_lot_data:
        logger.warning("No Purpose Lot Identifier data to merge")
        return

    tender = release_json.setdefault("tender", {})

    # Merge Lots
    existing_lots = tender.setdefault("lots", [])
    for new_lot in purpose_lot_data["tender"]["lots"]:
        if not any(lot["id"] == new_lot["id"] for lot in existing_lots):
            existing_lots.append(new_lot)

    # Merge Lots Groups
    existing_lot_groups = tender.setdefault("lotGroups", [])
    for new_group in purpose_lot_data["tender"]["lotGroups"]:
        if not any(group["id"] == new_group["id"] for group in existing_lot_groups):
            existing_lot_groups.append(new_group)

    # Merge Part
    if "id" in purpose_lot_data["tender"]:
        tender["id"] = purpose_lot_data["tender"]["id"]

    logger.info(f"Merged Purpose Lot Identifier data for {len(purpose_lot_data['tender']['lots'])} lots, "
                f"{len(purpose_lot_data['tender']['lotGroups'])} lot groups, "
                f"and {'1 part' if 'id' in purpose_lot_data['tender'] else '0 parts'}")