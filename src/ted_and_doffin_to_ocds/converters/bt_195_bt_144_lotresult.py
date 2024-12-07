# converters/bt_195_bt_144_LotResult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt144_unpublished_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse unpublished field identifiers for not awarded reason (BT-195, BT-144).

    For fields marked as unpublished:
    - Gets lot result ID
    - Creates withheld information entries with field details
    - Generates unique IDs by combining field code and lot result ID

    Args:
        xml_content: XML content containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing withheld information, or None if no data.
        Example structure:
        {
            "withheldInformation": [
                {
                    "id": "no-awa-rea-result_id",
                    "field": "no-awa-rea",
                    "name": "Not Awarded Reason"
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

    lot_results = root.xpath(
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension"
        "/efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        lot_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        field_identifier = lot_result.xpath(
            "efac:DecisionReason/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='no-awa-rea']"
            "/efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lot_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_id[0]}",
                "field": "no-awa-rea",
                "name": "Not Awarded Reason",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt144_unpublished_identifier(
    release_json: dict[str, Any], unpublished_data: dict[str, Any] | None
) -> None:
    """
    Merge unpublished not awarded reason data into the release JSON.

    Args:
        release_json: Target release JSON to update
        unpublished_data: Unpublished field data to merge

    Effects:
        Updates the withheldInformation section of release_json with
        unpublished not awarded reason information
    """
    if not unpublished_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-144)")
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

    logger.info("Merged unpublished identifier data for BT-195(BT-144)")
