# converters/BT_195_BT_09_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def bt_195_parse_unpublished_identifier_bt_09_procedure(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the procedure.

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
        "//cbc:ContractFolderID/text()", namespaces=namespaces
    )
    if not contract_folder_id:
        logger.warning("ContractFolderID not found in the XML")
        return None

    contract_folder_id = contract_folder_id[0]

    field_privacy = root.xpath(
        "//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/efbc:FieldIdentifierCode",
        namespaces=namespaces,
    )

    if field_privacy:
        withheld_item = {
            "id": f"cro-bor-law-{contract_folder_id}",
            "field": "cro-bor-law",
            "name": "Cross Border Law",
        }
        result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None


def bt_195_merge_unpublished_identifier_bt_09_procedure(
    release_json, unpublished_identifier_data
):
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

    withheld_information = release_json.setdefault("withheldInformation", [])

    for item in unpublished_identifier_data["withheldInformation"]:
        existing_item = next(
            (x for x in withheld_information if x["id"] == item["id"]), None
        )
        if existing_item:
            existing_item.update(item)
        else:
            withheld_information.append(item)

    logger.info(
        f"Merged unpublished identifier data: {len(unpublished_identifier_data['withheldInformation'])} items"
    )
