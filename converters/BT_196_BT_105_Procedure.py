# converters/BT_196_BT_105_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_bt196_bt105_unpublished_justification(xml_content):
    """
    Parse the XML content to extract the unpublished justification description for the procedure type.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished justification data.
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

    result = {"withheldInformation": []}

    reason_description = root.xpath("//efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']/efbc:ReasonDescription/text()", namespaces=namespaces)

    if reason_description:
        withheld_info = {
            "field": "pro-typ",
            "rationale": reason_description[0]
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def merge_bt196_bt105_unpublished_justification(release_json, unpublished_justification_data):
    """
    Merge the parsed unpublished justification data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_justification_data (dict): The parsed unpublished justification data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_justification_data:
        logger.warning("No unpublished justification data to merge")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_item in unpublished_justification_data["withheldInformation"]:
        existing_item = next((item for item in withheld_info if item["field"] == new_item["field"]), None)
        if existing_item:
            existing_item["rationale"] = new_item["rationale"]
        else:
            withheld_info.append(new_item)

    logger.info("Merged unpublished justification data")