# converters/BT_651_Lot_Subcontracting_Tender_Indication.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_subcontracting_tender_indication(xml_content: bytes):
    """
    Parse the XML content to extract the subcontracting tender indication for each lot.

    Args:
        xml_content (bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed subcontracting tender indication data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "submissionTerms": {
                                  "subcontractingClauses": ["code"]
                              }
                          }
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    root = etree.fromstring(xml_content, parser=etree.XMLParser(encoding='utf-8'))
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"tender": {"lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        subcontracting_code = lot.xpath("cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:TenderSubcontractingRequirements/efbc:TenderSubcontractingRequirementsCode[@listName='subcontracting-indication']/text()", namespaces=namespaces)
        
        if subcontracting_code:
            lot_data = {
                "id": lot_id,
                "submissionTerms": {
                    "subcontractingClauses": subcontracting_code
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_subcontracting_tender_indication(release_json, subcontracting_tender_indication_data):
    """
    Merge the parsed subcontracting tender indication data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        subcontracting_tender_indication_data (dict): The parsed subcontracting tender indication data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not subcontracting_tender_indication_data:
        logger.warning("No subcontracting tender indication data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])
    
    for new_lot in subcontracting_tender_indication_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            submission_terms = existing_lot.setdefault("submissionTerms", {})
            existing_clauses = submission_terms.setdefault("subcontractingClauses", [])
            existing_clauses.extend(new_lot["submissionTerms"]["subcontractingClauses"])
            # Remove duplicates while preserving order
            submission_terms["subcontractingClauses"] = list(dict.fromkeys(existing_clauses))
        else:
            existing_lots.append(new_lot)

    logger.info(f"Merged subcontracting tender indication data for {len(subcontracting_tender_indication_data['tender']['lots'])} lots")