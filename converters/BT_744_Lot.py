# converters/BT_744_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_submission_electronic_signature(xml_content):
    """
    Parse the XML content to extract the submission electronic signature requirement for each lot.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed submission electronic signature requirement data.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lots": []}}

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']"
    lots = root.xpath(xpath_query, namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        esignature_code = lot.xpath(".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='esignature-submission']/cbc:ExecutionRequirementCode/text()", namespaces=namespaces)
        
        if esignature_code:
            lot_data = {
                "id": lot_id,
                "submissionTerms": {
                    "advancedElectronicSignatureRequired": esignature_code[0].lower() == 'true'
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_submission_electronic_signature(release_json, submission_electronic_signature_data):
    """
    Merge the parsed submission electronic signature requirement data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        submission_electronic_signature_data (dict): The parsed submission electronic signature requirement data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not submission_electronic_signature_data:
        logger.warning("No submission electronic signature requirement data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in submission_electronic_signature_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(new_lot["submissionTerms"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged submission electronic signature requirement data for {len(submission_electronic_signature_data['tender']['lots'])} lots")