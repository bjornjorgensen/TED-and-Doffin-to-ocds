# converters/BT_195_BT_1252_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def BT_195_parse_unpublished_procedure_identifier_BT_1252(xml_content):
    """
    Parse the XML content to extract the unpublished procedure identifier (BT-195, BT-1252).

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished procedure identifier data.
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

    contract_folder_id = root.xpath("//cbc:ContractFolderID/text()", namespaces=namespaces)
    if not contract_folder_id:
        logger.warning("ContractFolderID not found")
        return None

    contract_folder_id = contract_folder_id[0]

    fields_privacy = root.xpath("//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='dir-awa-pre']/efbc:FieldIdentifierCode", namespaces=namespaces)

    if fields_privacy:
        withheld_info = {
            "id": f"dir-awa-pre-{contract_folder_id}",
            "field": "dir-awa-pre",
            "name": "Direct Award Justification Previous Procedure Identifier"
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None

def BT_195_merge_unpublished_procedure_identifier_BT_1252(release_json, unpublished_procedure_data):
    """
    Merge the parsed unpublished procedure identifier data (BT-195, BT-1252) into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_procedure_data (dict): The parsed unpublished procedure identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_procedure_data:
        logger.warning("No unpublished procedure identifier data to merge")
        return

    existing_withheld_info = release_json.setdefault("withheldInformation", [])
    
    for new_info in unpublished_procedure_data["withheldInformation"]:
        existing_info = next((info for info in existing_withheld_info if info["id"] == new_info["id"]), None)
        if existing_info:
            existing_info.update(new_info)
        else:
            existing_withheld_info.append(new_info)

    logger.info(f"Merged unpublished procedure identifier data for {len(unpublished_procedure_data['withheldInformation'])} items")