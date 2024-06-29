# converters/BT_23.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def map_procurement_category(value):
    if value == "supplies":
        return "goods"
    return value

def parse_main_nature(xml_content):
    logger.info("Parsing BT-23: Main Nature")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {}}

    # Parse BT-23-Lot
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    lots = []
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        main_nature = lot.xpath("cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)
        if main_nature:
            lots.append({
                "id": lot_id,
                "mainProcurementCategory": map_procurement_category(main_nature[0])
            })
    if lots:
        result["tender"]["lots"] = lots
    logger.debug(f"Parsed main nature for {len(lots)} lots")

    # Parse BT-23-Part
    part_nature = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()", namespaces=namespaces)
    if part_nature:
        result["tender"]["mainProcurementCategory"] = map_procurement_category(part_nature[0])
        logger.debug("Parsed main nature for Part")

    # Parse BT-23-Procedure
    procedure_nature = root.xpath("/*/cac:ProcurementProject/cbc:ProcurementTypeCode/text()", namespaces=namespaces)
    if procedure_nature:
        result["tender"]["mainProcurementCategory"] = map_procurement_category(procedure_nature[0])
        logger.debug("Parsed main nature for Procedure")

    return result

def merge_main_nature(release_json, main_nature_data):
    logger.info("Merging BT-23: Main Nature")
    if "tender" not in main_nature_data:
        logger.warning("No main nature data to merge")
        return

    tender = release_json.setdefault("tender", {})

    # Merge lots
    if "lots" in main_nature_data["tender"]:
        existing_lots = tender.setdefault("lots", [])
        for new_lot in main_nature_data["tender"]["lots"]:
            existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
            if existing_lot:
                existing_lot["mainProcurementCategory"] = new_lot["mainProcurementCategory"]
            else:
                existing_lots.append(new_lot)
        logger.debug(f"Merged main nature for {len(main_nature_data['tender']['lots'])} lots")

    # Merge tender mainProcurementCategory (Part and Procedure)
    if "mainProcurementCategory" in main_nature_data["tender"]:
        tender["mainProcurementCategory"] = main_nature_data["tender"]["mainProcurementCategory"]
        logger.debug("Merged main nature for tender")

    logger.info("Finished merging BT-23: Main Nature")