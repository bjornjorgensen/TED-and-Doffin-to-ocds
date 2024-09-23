# converters/bt_195_bt_710_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt710_unpublished_identifier(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the tender lowest value.

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
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    lot_results = root.xpath(
        "//efac:noticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        field_identifier = lot_result.xpath(
            "efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='ten-val-low']/efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )

        if field_identifier and lot_id:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_id[0]}",
                "field": "ten-val-low",
                "name": "Tender Lowest Value",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt710_unpublished_identifier(release_json, unpublished_identifier_data):
    """
    Merge the parsed unpublished identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-710)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        f"Merged {len(unpublished_identifier_data['withheldInformation'])} unpublished identifier(s) for BT-195(BT-710)",
    )
