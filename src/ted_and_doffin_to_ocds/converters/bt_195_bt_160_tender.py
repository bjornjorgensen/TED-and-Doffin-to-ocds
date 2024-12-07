# converters/bt_195_bt_160_Tender.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt160_unpublished_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse unpublished field identifiers for concession revenue (BT-195, BT-160).

    For fields marked as unpublished:
    - Gets lot tender ID
    - Creates withheld information entries with field details
    - Generates unique IDs by combining field code and tender ID

    Args:
        xml_content: XML content containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing withheld information, or None if no data.
        Example structure:
        {
            "withheldInformation": [
                {
                    "id": "con-rev-buy-tender_id",
                    "field": "con-rev-buy",
                    "name": "Concession Revenue Buyer"
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

    lot_tenders = root.xpath(
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension"
        "/efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        lot_tender_id = lot_tender.xpath(
            "cbc:ID/text()",
            namespaces=namespaces,
        )
        field_identifier = lot_tender.xpath(
            "efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='con-rev-buy']"
            "/efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lot_tender_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_tender_id[0]}",
                "field": "con-rev-buy",
                "name": "Concession Revenue Buyer",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt160_unpublished_identifier(
    release_json: dict[str, Any], unpublished_data: dict[str, Any] | None
) -> None:
    """
    Merge unpublished concession revenue data into the release JSON.

    Args:
        release_json: Target release JSON to update
        unpublished_data: Unpublished field data to merge

    Effects:
        Updates the withheldInformation section of release_json with
        unpublished concession revenue information
    """
    if not unpublished_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-160)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_data["withheldInformation"])

    logger.info(
        "Merged unpublished identifier data for BT-195(BT-160): %d items",
        len(unpublished_data["withheldInformation"]),
    )
