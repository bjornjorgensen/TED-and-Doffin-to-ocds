# converters/BT_7220_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lot_eu_funds(xml_content):
    """
    Parse the XML content to extract lot EU funds programme information.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed lot EU funds data.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes 
    if isinstance(xml_content, str): 
        xml_content = xml_content.encode('utf-8')

    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"lots": []}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        funding_programs = lot.xpath("cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:Funding/cbc:FundingProgramCode[@listName='eu-programme']/text()", namespaces=namespaces)

        if lot_id and funding_programs:
            lot_data = {
                "id": lot_id[0],
                "planning": {
                    "budget": {
                        "finance": [{"id": str(i+1), "title": program} for i, program in enumerate(funding_programs)]
                    }
                }
            }
            result["lots"].append(lot_data)

    return result if result["lots"] else None

def merge_lot_eu_funds(release_json, lot_eu_funds_data):
    """
    Merge the parsed lot EU funds data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_eu_funds_data (dict): The parsed lot EU funds data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_eu_funds_data:
        logger.warning("No lot EU funds data to merge")
        return

    if "lots" not in release_json:
        release_json["lots"] = []

    for new_lot in lot_eu_funds_data["lots"]:
        existing_lot = next((lot for lot in release_json["lots"] if lot["id"] == new_lot["id"]), None)
        if existing_lot:
            if "planning" not in existing_lot:
                existing_lot["planning"] = {}
            if "budget" not in existing_lot["planning"]:
                existing_lot["planning"]["budget"] = {}
            if "finance" not in existing_lot["planning"]["budget"]:
                existing_lot["planning"]["budget"]["finance"] = []
            
            # Merge new finance data with existing finance data
            for new_finance in new_lot["planning"]["budget"]["finance"]:
                existing_finance = next((f for f in existing_lot["planning"]["budget"]["finance"] if f["id"] == new_finance["id"]), None)
                if existing_finance:
                    existing_finance.update(new_finance)
                else:
                    existing_lot["planning"]["budget"]["finance"].append(new_finance)
        else:
            release_json["lots"].append(new_lot)

    logger.info(f"Merged lot EU funds data for {len(lot_eu_funds_data['lots'])} lots")