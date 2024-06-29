# converters/BT_93_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_electronic_payment(xml_content):
    logger.info("Parsing BT-93-Lot: Electronic Payment")
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
        electronic_payment = lot.xpath(
            "cac:TenderingTerms/cac:PostAwardProcess/cbc:ElectronicPaymentUsageIndicator/text()",
            namespaces=namespaces
        )
        
        if electronic_payment:
            has_electronic_payment = electronic_payment[0].lower() == 'true'
            logger.debug(f"Lot {lot_id} has Electronic Payment: {has_electronic_payment}")
            result["tender"]["lots"].append({
                "id": lot_id,
                "contractTerms": {
                    "hasElectronicPayment": has_electronic_payment
                }
            })
        else:
            logger.debug(f"No Electronic Payment information found for lot {lot_id}")

    logger.info(f"Parsed Electronic Payment for {len(result['tender']['lots'])} lots")
    return result

def merge_electronic_payment(release_json, electronic_payment_data):
    logger.info("Merging BT-93-Lot: Electronic Payment")
    if not electronic_payment_data["tender"]["lots"]:
        logger.warning("No Electronic Payment data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for ep_lot in electronic_payment_data["tender"]["lots"]:
        lot_id = ep_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)
        
        if existing_lot:
            existing_lot.setdefault("contractTerms", {})["hasElectronicPayment"] = ep_lot["contractTerms"]["hasElectronicPayment"]
            logger.debug(f"Updated Electronic Payment for existing lot {lot_id}")
        else:
            lots.append(ep_lot)
            logger.debug(f"Added new lot {lot_id} with Electronic Payment information")

    logger.info(f"Merged Electronic Payment for {len(electronic_payment_data['tender']['lots'])} lots")