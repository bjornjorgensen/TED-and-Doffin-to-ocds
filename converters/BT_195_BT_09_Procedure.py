# converters/BT_195_BT_09_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def bt_195_parse_unpublished_cross_border_law_bt_09(xml_content):
    """
    Parse the XML content to extract the unpublished cross border law identifier for the procedure.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished cross border law identifier data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    contract_folder_id = root.xpath("//cbc:ContractFolderID/text()", namespaces=namespaces)
    field_identifier_code = root.xpath("//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/efbc:FieldIdentifierCode/text()", namespaces=namespaces)

    if contract_folder_id and field_identifier_code:
        return {
            "withheldInformation": [{
                "id": f"{field_identifier_code[0]}-{contract_folder_id[0]}",
                "field": field_identifier_code[0],
                "name": "Cross Border Law"
            }]
        }

    return None

def bt_195_merge_unpublished_cross_border_law_bt_09(release_json, unpublished_identifier_data):
    """
    Merge the parsed unpublished cross border law identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished cross border law identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished cross border law identifier data to merge")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info("Merged unpublished cross border law identifier data")