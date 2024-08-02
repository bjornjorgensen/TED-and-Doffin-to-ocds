# converters/BT_63_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

VARIANT_POLICY_MAPPING = {
    "required": "Required",
    "allowed": "Allowed",
    "notAllowed": "Not allowed"
}

def parse_variants(xml_content):
    """
    Parse the XML content to extract variant policy information for each lot.

    This function processes the BT-63-Lot business term, which represents
    whether tenderers are required, allowed, or not allowed to submit tenders
    which fulfil the buyer's needs differently than as proposed in the procurement documents.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed variant policy data in the format:
              {
                  "tender": {
                      "lots": [
                          {
                              "id": "lot_id",
                              "submissionTerms": {
                                  "variantPolicy": "policy"
                              }
                          }
                      ]
                  }
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
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

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        variant_constraint = lot.xpath("cac:TenderingTerms/cbc:VariantConstraintCode[@listName='permission']/text()", namespaces=namespaces)
        
        if variant_constraint:
            variant_policy = VARIANT_POLICY_MAPPING.get(variant_constraint[0], "Unknown")
            lot_data = {
                "id": lot_id,
                "submissionTerms": {
                    "variantPolicy": variant_policy
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_variants(release_json, variants_data):
    """
    Merge the parsed variant policy data into the main OCDS release JSON.

    This function updates the existing lots in the release JSON with the
    variant policy information. If a lot doesn't exist, it adds a new lot to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        variants_data (dict): The parsed variant policy data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not variants_data:
        logger.warning("BT-63-Lot: No variant policy data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])
    
    for new_lot in variants_data["tender"]["lots"]:
        existing_lot = next((lot for lot in existing_lots if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(new_lot["submissionTerms"])
        else:
            existing_lots.append(new_lot)

    logger.info(f"BT-63-Lot: Merged variant policy data for {len(variants_data['tender']['lots'])} lots")