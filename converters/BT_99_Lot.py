# converters/BT_99_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_review_deadline_description(xml_content):
    logger.info("Parsing BT-99-Lot: Review Deadline Description")
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"tender": {"lots": []}}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        review_description = lot.xpath("cac:TenderingTerms/cac:AppealTerms/cac:PresentationPeriod/cbc:Description/text()", namespaces=namespaces)
        
        if review_description:
            result["tender"]["lots"].append({
                "id": lot_id,
                "reviewDetails": review_description[0]
            })
            logger.debug(f"Parsed Review Deadline Description for lot {lot_id}")
        else:
            logger.debug(f"No Review Deadline Description found for lot {lot_id}")

    return result

def merge_review_deadline_description(release_json, review_deadline_data):
    logger.info("Merging BT-99-Lot: Review Deadline Description")
    if not review_deadline_data["tender"]["lots"]:
        logger.warning("No Review Deadline Description data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for new_lot in review_deadline_data["tender"]["lots"]:
        existing_lot = next((lot for lot in lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot["reviewDetails"] = new_lot["reviewDetails"]
            logger.debug(f"Updated Review Deadline Description for existing lot {new_lot['id']}")
        else:
            lots.append(new_lot)
            logger.debug(f"Added new lot {new_lot['id']} with Review Deadline Description")

    logger.info(f"Merged Review Deadline Description for {len(review_deadline_data['tender']['lots'])} lots")