# converters/bt_195_bt_105_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt105_unpublished_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse unpublished field identifiers for procedure type (BT-195, BT-105).

    For fields marked as unpublished:
    - Gets ContractFolderID
    - Creates withheld information entries for procedure type
    - Generates unique IDs by combining field code and folder ID

    Args:
        xml_content: XML content containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing withheld information, or None if no data.
        Example structure:
        {
            "withheldInformation": [
                {
                    "id": "pro-typ-contract_folder_id",
                    "field": "pro-typ",
                    "name": "Procedure Type"
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

    result = {"withheldInformation": []}

    contract_folder_id = root.xpath(
        "/*/cbc:ContractFolderID/text()",
        namespaces=namespaces,
    )
    field_identifier = root.xpath(
        "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
        "/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']"
        "/efbc:FieldIdentifierCode/text()",
        namespaces=namespaces,
    )

    if contract_folder_id and field_identifier:
        withheld_info = {
            "id": f"{field_identifier[0]}-{contract_folder_id[0]}",
            "field": "pro-typ",
            "name": "Procedure Type",
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt105_unpublished_identifier(
    release_json, unpublished_identifier_data
) -> None:
    """Merge the parsed unpublished identifier data into the main OCDS release JSON.

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

    logger.info("Merged unpublished identifier data")
