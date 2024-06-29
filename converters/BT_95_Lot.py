# converters/BT_95_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_recurrence_description(xml_content):
    logger.info("Parsing BT-95-Lot: Recurrence Description")
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
        recurrence_description = lot.xpath(
            "cac:TenderingTerms/cbc:RecurringProcurementDescription/text()",
            namespaces=namespaces
        )
        
        if recurrence_description:
            logger.debug(f"Lot {lot_id} has Recurrence Description")
            result["tender"]["lots"].append({
                "id": lot_id,
                "recurrence": {
                    "description": recurrence_description[0]
                }
            })
        else:
            logger.debug(f"No Recurrence Description found for lot {lot_id}")

    logger.info(f"Parsed Recurrence Description for {len(result['tender']['lots'])} lots")
    return result

def merge_recurrence_description(release_json, recurrence_description_data):
    logger.info("Merging BT-95-Lot: Recurrence Description")
    if not recurrence_description_data["tender"]["lots"]:
        logger.warning("No Recurrence Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for rec_lot in recurrence_description_data["tender"]["lots"]:
        lot_id = rec_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)
        
        if existing_lot:
            existing_lot.setdefault("recurrence", {})["description"] = rec_lot["recurrence"]["description"]
            logger.debug(f"Updated Recurrence Description for existing lot {lot_id}")
        else:
            lots.append(rec_lot)
            logger.debug(f"Added new lot {lot_id} with Recurrence Description")

    logger.info(f"Merged Recurrence Description for {len(recurrence_description_data['tender']['lots'])} lots")