# converters/BT_763_LotsAllRequired.py

import logging
from typing import Optional, Dict
from lxml import etree

logger = logging.getLogger(__name__)

def parse_lots_all_required(xml_content: str) -> Optional[Dict]:
    """
    Parse the XML content to extract the PartPresentationCode for Lots All Required.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data if 'all' is specified, None otherwise.
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

    part_presentation_code = root.xpath("//cac:TenderingProcess/cbc:PartPresentationCode[@listName='tenderlot-presentation']/text()", namespaces=namespaces)

    if part_presentation_code and part_presentation_code[0].lower() == 'all':
        return {"tender": {"lotDetails": {"maximumLotsBidPerSupplier": 1e9999}}}
    
    return None

def merge_lots_all_required(release_json: Dict, lots_all_required_data: Optional[Dict]) -> None:
    """
    Merge the parsed Lots All Required data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        lots_all_required_data (Optional[Dict]): The parsed Lots All Required data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if lots_all_required_data:
        tender = release_json.setdefault("tender", {})
        tender["lotDetails"] = lots_all_required_data["tender"]["lotDetails"]
        logger.info("Merged Lots All Required data")
    else:
        logger.info("No Lots All Required data to merge")