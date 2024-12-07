# converters/bt_195_bt_09_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def bt_195_parse_unpublished_identifier_bt_09_procedure(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse unpublished field identifiers for cross border law.

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
                    "id": "field_code-contract_folder_id",
                    "field": "field_code",
                    "name": "Field Name"
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
        "//cbc:ContractFolderID/text()",
        namespaces=namespaces,
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
    release_json: dict[str, Any], unpublished_data: dict[str, Any] | None
) -> None:
    """
    Merge unpublished cross border law data into the release JSON.

    Args:
        release_json: Target release JSON to update
        unpublished_data: Unpublished field data to merge

    Effects:
        Updates the withheldInformation section of release_json with
        unpublished field references
    """
    if not unpublished_data:
        logger.warning("No unpublished cross border law data to merge")
        return

    withheld_information = release_json.setdefault("withheldInformation", [])

    for item in unpublished_data["withheldInformation"]:
        existing_item = next(
            (x for x in withheld_information if x["id"] == item["id"]),
            None,
        )
        if existing_item:
            existing_item.update(item)
        else:
            withheld_information.append(item)

    logger.info(
        "Merged unpublished cross border law data: %d items",
        len(unpublished_data["withheldInformation"]),
    )
