import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt88_procedure_unpublished_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse unpublished field identifiers for procedure features (BT-195, BT-88).

    For fields marked as unpublished:
    - Gets ContractFolderID
    - Creates withheld information for procedure features
    - Generates unique IDs by combining field code and folder ID

    Args:
        xml_content: XML content containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing withheld information, or None if no data.
        Example structure:
        {
            "withheldInformation": [
                {
                    "id": "pro-fea-contract_folder_id",
                    "field": "pro-fea",
                    "name": "Procedure Features"
                }
            ]
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML")
        return None

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    # Get ContractFolderID
    contract_folder_id_elements = root.xpath(
        "/*/cbc:ContractFolderID", namespaces=namespaces
    )
    if not contract_folder_id_elements:
        logger.warning("ContractFolderID not found in the XML")
        return None

    contract_folder_id = contract_folder_id_elements[0].text
    if not contract_folder_id:
        logger.warning("ContractFolderID element exists but contains no value")
        return None

    # Find procedure features privacy elements
    xpath_query = (
        "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
        "/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-fea']"
    )

    fields_privacy_elements = root.xpath(xpath_query, namespaces=namespaces)
    if not fields_privacy_elements:
        logger.debug("No procedure features privacy elements found")
        return None

    # Create withheld information for each found element
    for _field_privacy in fields_privacy_elements:
        # Create withheld information entry according to eForms guidance
        withheld_info = {
            "id": f"pro-fea-{contract_folder_id}",
            "field": "pro-fea",
            "name": "Procedure Features",
        }
        result["withheldInformation"].append(withheld_info)
        logger.debug(
            "Added withheld information for procedure features with ID: %s",
            withheld_info["id"],
        )

    return result if result["withheldInformation"] else None


def merge_bt195_bt88_procedure_unpublished_identifier(
    release_json: dict[str, Any], unpublished_data: dict[str, Any] | None
) -> None:
    """Merge unpublished procedure features data into the release JSON.

    Args:
        release_json: Target release JSON to update
        unpublished_data: Unpublished field data to merge

    Effects:
        Updates the withheldInformation section of release_json with
        unpublished procedure features

    """
    if not unpublished_data:
        logger.warning(
            "No unpublished identifier data to merge for BT-195(BT-88)-procedure",
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item.update(new_item)
        else:
            withheld_info.append(new_item)

    logger.info(
        "Merged unpublished procedure features data: %d items",
        len(unpublished_data["withheldInformation"]) if unpublished_data else 0,
    )
