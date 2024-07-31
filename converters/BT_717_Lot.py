# converters/BT_717_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_clean_vehicles_directive(xml_content):
    """
    Parse the XML content to extract the Clean Vehicles Directive applicability for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed data in the format:
              {
                  "LOT-ID": bool
              }
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

    result = {}

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        applicable_legal_basis = lot.xpath(".//efac:StrategicProcurement/efbc:ApplicableLegalBasis[@listName='cvd-scope']/text()", namespaces=namespaces)
        
        if applicable_legal_basis:
            result[lot_id] = applicable_legal_basis[0].lower() == 'true'

    return result if result else None

def merge_clean_vehicles_directive(release_json, clean_vehicles_directive_data):
    """
    Merge the parsed Clean Vehicles Directive data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        clean_vehicles_directive_data (dict): The parsed Clean Vehicles Directive data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not clean_vehicles_directive_data:
        logger.warning("No Clean Vehicles Directive data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot in lots:
        lot_id = lot["id"]
        if lot_id in clean_vehicles_directive_data and clean_vehicles_directive_data[lot_id]:
            lot.setdefault("coveredBy", []).append("EU-CVD")

    logger.info(f"Merged Clean Vehicles Directive data for {len(clean_vehicles_directive_data)} lots")