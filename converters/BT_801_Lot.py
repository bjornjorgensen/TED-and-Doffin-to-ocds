# converters/BT_801_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_non_disclosure_agreement(xml_content):
    logger.info("Parsing BT-801-Lot: Non Disclosure Agreement")
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
        nda_element = lot.xpath(
            "cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='nda']/cbc:ExecutionRequirementCode/text()",
            namespaces=namespaces
        )
        
        if nda_element:
            has_nda = nda_element[0].lower() == 'true'
            logger.debug(f"Lot {lot_id} has NDA: {has_nda}")
            result["tender"]["lots"].append({
                "id": lot_id,
                "contractTerms": {
                    "hasNonDisclosureAgreement": has_nda
                }
            })
        else:
            logger.debug(f"No NDA information found for lot {lot_id}")

    logger.info(f"Parsed NDA information for {len(result['tender']['lots'])} lots")
    return result

def merge_non_disclosure_agreement(release_json, nda_data):
    logger.info("Merging BT-801-Lot: Non Disclosure Agreement")
    if not nda_data["tender"]["lots"]:
        logger.warning("No NDA data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for nda_lot in nda_data["tender"]["lots"]:
        lot_id = nda_lot["id"]
        existing_lot = next((lot for lot in lots if lot["id"] == lot_id), None)
        
        if existing_lot:
            existing_lot.setdefault("contractTerms", {})["hasNonDisclosureAgreement"] = nda_lot["contractTerms"]["hasNonDisclosureAgreement"]
            logger.debug(f"Updated NDA information for existing lot {lot_id}")
        else:
            lots.append(nda_lot)
            logger.debug(f"Added new lot {lot_id} with NDA information")

    logger.info(f"Merged NDA information for {len(nda_data['tender']['lots'])} lots")