# converters/BT_94_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_recurrence(xml_content):
    logger.info("Parsing BT-94-Lot: Recurrence")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    logger.debug(f"Found {len(lot_elements)} lot elements")
    
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        recurrence = lot.xpath(
            "cac:TenderingTerms/cbc:RecurringProcurementIndicator/text()",
            namespaces=namespaces
        )
        
        if recurrence:
            has_recurrence = recurrence[0].lower() == 'true'
            logger.debug(f"Lot {lot_id} has Recurrence: {has_recurrence}")
            result["tender"]["lots"].append({
                "id": lot_id,
                "hasRecurrence": has_recurrence
            })
        else:
            logger.debug(f"No Recurrence information found for lot {lot_id}")

    logger.info(f"Parsed Recurrence for {len(result['tender']['lots'])} lots")
    return result

def merge_recurrence(release_json, recurrence_data):
    logger.info("Merging BT-94-Lot: Recurrence")
    if not recurrence_data["tender"]["lots"]:
        logger.warning("No Recurrence data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for rec_lot in recurrence_data["tender"]["lots"]:
        lot_id = rec_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)
        
        if existing_lot:
            existing_lot["hasRecurrence"] = rec_lot["hasRecurrence"]
            logger.debug(f"Updated Recurrence for existing lot {lot_id}")
        else:
            lots.append(rec_lot)
            logger.debug(f"Added new lot {lot_id} with Recurrence information")

    logger.info(f"Merged Recurrence for {len(recurrence_data['tender']['lots'])} lots")