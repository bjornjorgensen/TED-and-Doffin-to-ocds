# converters/BT_92_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_electronic_ordering(xml_content):
    logger.info("Parsing BT-92-Lot: Electronic Ordering")
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
        electronic_ordering = lot.xpath(
            "cac:TenderingTerms/cac:PostAwardProcess/cbc:ElectronicOrderUsageIndicator/text()",
            namespaces=namespaces
        )
        
        if electronic_ordering:
            has_electronic_ordering = electronic_ordering[0].lower() == 'true'
            logger.debug(f"Lot {lot_id} has Electronic Ordering: {has_electronic_ordering}")
            result["tender"]["lots"].append({
                "id": lot_id,
                "contractTerms": {
                    "hasElectronicOrdering": has_electronic_ordering
                }
            })
        else:
            logger.debug(f"No Electronic Ordering information found for lot {lot_id}")

    logger.info(f"Parsed Electronic Ordering for {len(result['tender']['lots'])} lots")
    return result

def merge_electronic_ordering(release_json, electronic_ordering_data):
    logger.info("Merging BT-92-Lot: Electronic Ordering")
    if not electronic_ordering_data["tender"]["lots"]:
        logger.warning("No Electronic Ordering data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for eo_lot in electronic_ordering_data["tender"]["lots"]:
        lot_id = eo_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)
        
        if existing_lot:
            existing_lot.setdefault("contractTerms", {})["hasElectronicOrdering"] = eo_lot["contractTerms"]["hasElectronicOrdering"]
            logger.debug(f"Updated Electronic Ordering for existing lot {lot_id}")
        else:
            lots.append(eo_lot)
            logger.debug(f"Added new lot {lot_id} with Electronic Ordering information")

    logger.info(f"Merged Electronic Ordering for {len(electronic_ordering_data['tender']['lots'])} lots")