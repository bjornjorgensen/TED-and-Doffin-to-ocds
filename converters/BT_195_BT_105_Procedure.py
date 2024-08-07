# converters/BT_195_BT_105_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def bt_195_parse_unpublished_procedure_type_bt_105(xml_content):
    """
    Parse the XML content to extract the unpublished procedure type identifier.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished procedure type identifier data.
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
    field_identifier_code = root.xpath("//cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']/efbc:FieldIdentifierCode/text()", namespaces=namespaces)

    if contract_folder_id and field_identifier_code:
        return {
            "withheldInformation": [{
                "id": f"{field_identifier_code[0]}-{contract_folder_id[0]}",
                "field": field_identifier_code[0],
                "name": "Procedure Type"
            }]
        }

    return None

def bt_195_merge_unpublished_procedure_type_bt_105(release_json, unpublished_identifier_data):
    """
    Merge the parsed unpublished procedure type identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished procedure type identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished procedure type identifier data to merge")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info("Merged unpublished procedure type identifier data")