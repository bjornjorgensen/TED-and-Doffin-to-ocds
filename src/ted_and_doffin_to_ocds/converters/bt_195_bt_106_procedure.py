# converters/bt_195_bt_106_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt106_unpublished_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse unpublished field identifiers for procedure accelerated (BT-195, BT-106).

    For fields marked as unpublished:
    - Gets ContractFolderID
    - Creates withheld information for procedure accelerated
    - Generates unique IDs by combining field code and folder ID

    Args:
        xml_content: XML content containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing withheld information, or None if no data.
        Example structure:
        {
            "withheldInformation": [
                {
                    "id": "pro-acc-contract_folder_id",
                    "field": "pro-acc",
                    "name": "Procedure Accelerated"
                }
            ]
        }

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

    relevant_xpath = (
        "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']"
        "/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension"
        "/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc']/efbc:FieldIdentifierCode/text()"
    )
    if not root.xpath(relevant_xpath, namespaces=namespaces):
        logger.info(
            "No unpublished identifier data found for BT-195(BT-106). Skipping parse_bt195_bt106_unpublished_identifier."
        )
        return None

    result = {"withheldInformation": []}

    contract_folder_id = root.xpath(
        "/*/cbc:ContractFolderID/text()",
        namespaces=namespaces,
    )
    field_identifier = root.xpath(
        relevant_xpath,
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


def merge_bt195_bt106_unpublished_identifier(
    release_json: dict[str, Any], unpublished_data: dict[str, Any] | None
) -> None:
    """Merge unpublished procedure accelerated data into the release JSON.

    Args:
        release_json: Target release JSON to update
        unpublished_data: Unpublished field data to merge

    Effects:
        Updates the withheldInformation section of release_json with
        unpublished procedure accelerated information

    """
    if not unpublished_data:
        logger.info("No unpublished identifier data to merge for BT-195(BT-106)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_data["withheldInformation"])

    logger.info("Merged unpublished identifier data for BT-195(BT-106)")
