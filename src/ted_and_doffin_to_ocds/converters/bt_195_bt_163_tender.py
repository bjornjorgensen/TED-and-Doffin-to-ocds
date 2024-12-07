# converters/bt_195_bt_163_Tender.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt163_unpublished_identifier(
    xml_content: str,
) -> dict[str, list] | None:
    """
    Parse the XML content to extract the unpublished identifier for the concession value description.

    This function processes XML content to find any tender lots where concession value description
    information is marked as private/unpublished. For each such lot, it creates a withheld
    information entry with a unique identifier.

    Args:
        xml_content (str): The XML content containing tender and lot information

    Returns:
        Optional[Dict[str, list]]: A dictionary containing a list of withheld information entries,
            where each entry has id, field and name properties. Returns None if no relevant
            data is found.

    Example:
        >>> result = parse_bt195_bt163_unpublished_identifier(xml_string)
        >>> print(result)
        {
            "withheldInformation": [
                {
                    "id": "val-con-des-TEN-0001",
                    "field": "val-con-des",
                    "name": "Concession Value Description"
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
        "//efac:noticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        lot_tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)
        field_identifier = lot_tender.xpath(
            "efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='val-con-des']/efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lot_tender_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_tender_id[0]}",
                "field": "val-con-des",
                "name": "Concession Value Description",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt163_unpublished_identifier(
    release_json: dict[str, Any], unpublished_identifier_data: dict[str, list] | None
) -> None:
    """
    Merge the parsed unpublished identifier data into the main OCDS release JSON.

    This function takes the withheld information entries identified by the parser and
    merges them into the main OCDS release JSON structure. It ensures the withheldInformation
    array exists and appends new entries to it.

    Args:
        release_json (Dict[str, Any]): The main OCDS release JSON document to be updated
        unpublished_identifier_data (Optional[Dict[str, list]]): The parsed unpublished identifier
            data containing withheld information entries to be merged

    Returns:
        None: The function modifies the release_json in-place

    Example:
        >>> release = {"id": "release-001"}
        >>> withheld_data = {
        ...     "withheldInformation": [
        ...         {
        ...             "id": "val-con-des-TEN-0001",
        ...             "field": "val-con-des",
        ...             "name": "Concession Value Description"
        ...         }
        ...     ]
        ... }
        >>> merge_bt195_bt163_unpublished_identifier(release, withheld_data)
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-163)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        "Merged unpublished identifier data for BT-195(BT-163): %d items",
        len(unpublished_identifier_data["withheldInformation"]),
    )
