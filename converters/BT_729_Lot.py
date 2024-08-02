# converters/BT_729_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_subcontracting_obligation_maximum(xml_content):
    """
    Parse the XML content to extract subcontracting obligation maximum percentage for lots.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed subcontracting obligation maximum percentage data for lots.
        None: If no relevant data is found.
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
        max_percent = lot.xpath("cac:TenderingTerms/cac:AllowedSubcontractTerms[cbc:SubcontractingConditionsCode/@listName='subcontracting-obligation']/cbc:MaximumPercent/text()", namespaces=namespaces)

        if max_percent:
            lot_data = {
                "id": lot_id,
                "subcontractingTerms": {
                    "competitiveMaximumPercentage": float(max_percent[0]) / 100
                }
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None

def merge_lot_subcontracting_obligation_maximum(release_json, lot_subcontracting_obligation_maximum_data):
    """
    Merge the parsed subcontracting obligation maximum percentage data for lots into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_subcontracting_obligation_maximum_data (dict): The parsed subcontracting obligation maximum percentage data for lots to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_subcontracting_obligation_maximum_data:
        logger.warning("No lot subcontracting obligation maximum percentage data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "lots" not in release_json["tender"]:
        release_json["tender"]["lots"] = []

    for new_lot in lot_subcontracting_obligation_maximum_data["tender"]["lots"]:
        existing_lot = next((lot for lot in release_json["tender"]["lots"] if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            if "subcontractingTerms" not in existing_lot:
                existing_lot["subcontractingTerms"] = {}
            existing_lot["subcontractingTerms"]["competitiveMaximumPercentage"] = new_lot["subcontractingTerms"]["competitiveMaximumPercentage"]
        else:
            release_json["tender"]["lots"].append(new_lot)

    logger.info(f"Merged subcontracting obligation maximum percentage data for {len(lot_subcontracting_obligation_maximum_data['tender']['lots'])} lots")