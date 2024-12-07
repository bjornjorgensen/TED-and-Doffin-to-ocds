# converters/bt_195_bt_136_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt136_unpublished_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse unpublished field identifiers for direct award justification (BT-195, BT-136).

    For fields marked as unpublished:
    - Gets ContractFolderID
    - Creates withheld information entries with field details
    - Generates unique IDs by combining field code and folder ID

    Args:
        xml_content: XML content containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing withheld information, or None if no data.
        Example structure:
        {
            "withheldInformation": [
                {
                    "id": "dir-awa-jus-contract_folder_id",
                    "field": "dir-awa-jus",
                    "name": "Direct Award Justification"
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
        "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']"
        "/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension"
        "/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='dir-awa-jus']/efbc:FieldIdentifierCode/text()",
        namespaces=namespaces,
    )

    if contract_folder_id and field_identifier:
        withheld_info = {
            "id": f"{field_identifier[0]}-{contract_folder_id[0]}",
            "field": "dir-awa-jus",
            "name": "Direct Award Justification",
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt136_unpublished_identifier(
    release_json: dict[str, Any], unpublished_data: dict[str, Any] | None
) -> None:
    """
    Merge unpublished direct award justification data into the release JSON.

    Args:
        release_json: Target release JSON to update
        unpublished_data: Unpublished field data to merge

    Effects:
        Updates the withheldInformation section of release_json with
        unpublished direct award justification information
    """
    if not unpublished_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-136)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_data["withheldInformation"])

    logger.info("Merged unpublished identifier data for BT-195(BT-136)")
