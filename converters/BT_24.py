# converters/BT_24.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_description(xml_content):
    logger.info("Parsing BT-24: Description")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    # Parse BT-24-Lot
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    lots = []
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot.xpath("cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
        if description:
            lots.append({
                "id": lot_id,
                "description": description[0]
            })
    if lots:
        result["tender"]["lots"] = lots
    logger.debug(f"Parsed description for {len(lots)} lots")

    # Parse BT-24-LotsGroup
    group_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    lot_groups = []
    for group in group_elements:
        group_id = group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = group.xpath("cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
        if description:
            lot_groups.append({
                "id": group_id,
                "description": description[0]
            })
    if lot_groups:
        result["tender"]["lotGroups"] = lot_groups
    logger.debug(f"Parsed description for {len(lot_groups)} lot groups")

    # Parse BT-24-Part
    part_description = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
    if part_description:
        result["tender"]["description"] = part_description[0]
        logger.debug("Parsed description for Part")

    # Parse BT-24-Procedure
    procedure_description = root.xpath("/*/cac:ProcurementProject/cbc:Description/text()", namespaces=namespaces)
    if procedure_description:
        result["tender"]["description"] = procedure_description[0]
        logger.debug("Parsed description for Procedure")

    return result

def merge_description(release_json, description_data):
    logger.info("Merging BT-24: Description")
    if "tender" not in description_data:
        logger.warning("No description data to merge")
        return

    tender = release_json.setdefault("tender", {})

    # Merge lots
    if "lots" in description_data["tender"]:
        existing_lots = tender.setdefault("lots", [])
        for new_lot in description_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot["description"] = new_lot["description"]
            else:
                existing_lots.append(new_lot)
        logger.debug(f"Merged description for {len(description_data['tender']['lots'])} lots")

    # Merge lot groups
    if "lotGroups" in description_data["tender"]:
        existing_groups = tender.setdefault("lotGroups", [])
        for new_group in description_data["tender"]["lotGroups"]:
            existing_group = next((group for group in existing_groups if group["id"] == new_group["id"]), None)
            if existing_group:
                existing_group["description"] = new_group["description"]
            else:
                existing_groups.append(new_group)
        logger.debug(f"Merged description for {len(description_data['tender']['lotGroups'])} lot groups")

    # Merge tender description (Part and Procedure)
    if "description" in description_data["tender"]:
        tender["description"] = description_data["tender"]["description"]
        logger.debug("Merged description for tender")

    logger.info("Finished merging BT-24: Description")