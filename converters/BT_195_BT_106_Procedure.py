# converters/BT_195_BT_106_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt106_unpublished_identifier(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the procedure accelerated.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished identifier data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    contract_folder_id = root.xpath(
        "/*/cbc:ContractFolderID/text()", namespaces=namespaces
    )
    field_identifier = root.xpath(
        "//cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc']/efbc:FieldIdentifierCode/text()",
        namespaces=namespaces,
    )

    if contract_folder_id and field_identifier:
        withheld_info = {
            "id": f"{field_identifier[0]}-{contract_folder_id[0]}",
            "field": "pro-acc",
            "name": "Procedure Accelerated",
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt106_unpublished_identifier(release_json, unpublished_identifier_data):
    """
    Merge the parsed unpublished identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info("Merged unpublished identifier data for BT-195(BT-106)")
