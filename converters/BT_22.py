# converters/BT_22.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_internal_identifiers(xml_content):
    logger.info("Parsing BT-22: Internal Identifiers")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    # Parse BT-22-Lot
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    lots = []
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        internal_id = lot.xpath("cac:ProcurementProject/cbc:ID/text()", namespaces=namespaces)
        if internal_id:
            lots.append({
                "id": lot_id,
                "identifiers": [{"id": internal_id[0], "scheme": "internal"}]
            })
    if lots:
        result["tender"]["lots"] = lots
    logger.debug(f"Parsed {len(lots)} lots with internal identifiers")

    # Parse BT-22-LotsGroup
    group_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    lot_groups = []
    for group in group_elements:
        group_id = group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        internal_id = group.xpath("cac:ProcurementProject/cbc:ID/text()", namespaces=namespaces)
        if internal_id:
            lot_groups.append({
                "id": group_id,
                "identifiers": [{"id": internal_id[0], "scheme": "internal"}]
            })
    if lot_groups:
        result["tender"]["lotGroups"] = lot_groups
    logger.debug(f"Parsed {len(lot_groups)} lot groups with internal identifiers")

    # Parse BT-22-Part and BT-22-Procedure
    identifiers = []
    part_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:ID/text()", namespaces=namespaces)
    if part_elements:
        identifiers.append({"id": part_elements[0], "scheme": "internal"})
        logger.debug("Parsed Part internal identifier")

    procedure_elements = root.xpath("/*/cac:ProcurementProject/cbc:ID/text()", namespaces=namespaces)
    if procedure_elements:
        identifiers.append({"id": procedure_elements[0], "scheme": "internal"})
        logger.debug("Parsed Procedure internal identifier")

    if identifiers:
        result["tender"]["identifiers"] = identifiers

    return result

def merge_internal_identifiers(release_json, internal_identifiers_data):
    logger.info("Merging BT-22: Internal Identifiers")
    if "tender" not in internal_identifiers_data:
        logger.warning("No internal identifiers data to merge")
        return

    tender = release_json.setdefault("tender", {})

    # Merge lots
    if "lots" in internal_identifiers_data["tender"]:
        existing_lots = tender.setdefault("lots", [])
        for new_lot in internal_identifiers_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot.setdefault("identifiers", []).extend(new_lot["identifiers"])
            else:
                existing_lots.append(new_lot)
        logger.debug(f"Merged internal identifiers for {len(internal_identifiers_data['tender']['lots'])} lots")

    # Merge lot groups
    if "lotGroups" in internal_identifiers_data["tender"]:
        existing_groups = tender.setdefault("lotGroups", [])
        for new_group in internal_identifiers_data["tender"]["lotGroups"]:
            existing_group = next((group for group in existing_groups if group["id"] == new_group["id"]), None)
            if existing_group:
                existing_group.setdefault("identifiers", []).extend(new_group["identifiers"])
            else:
                existing_groups.append(new_group)
        logger.debug(f"Merged internal identifiers for {len(internal_identifiers_data['tender']['lotGroups'])} lot groups")

    # Merge tender identifiers (Part and Procedure)
    if "identifiers" in internal_identifiers_data["tender"]:
        existing_identifiers = tender.setdefault("identifiers", [])
        for new_identifier in internal_identifiers_data["tender"]["identifiers"]:
            if new_identifier not in existing_identifiers:
                existing_identifiers.append(new_identifier)
        logger.debug(f"Merged {len(internal_identifiers_data['tender']['identifiers'])} tender internal identifiers")

    logger.info("Finished merging BT-22: Internal Identifiers")