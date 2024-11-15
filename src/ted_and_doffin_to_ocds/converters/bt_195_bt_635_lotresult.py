# converters/bt_195_bt_635_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt635_unpublished_identifier(xml_content):
    """
    Parse the XML content to extract the unpublished identifier for the buyer review request count.

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

    xpath_query = "//efac:noticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='buy-rev-cou']"
    appeal_requests_statistics = root.xpath(xpath_query, namespaces=namespaces)

    for statistic in appeal_requests_statistics:
        lot_result_id = statistic.xpath(
            "ancestor::efac:LotResult/cbc:ID/text()",
            namespaces=namespaces,
        )
        field_identifier = statistic.xpath(
            "efbc:FieldIdentifierCode/text()",
            namespaces=namespaces,
        )

        if lot_result_id and field_identifier:
            withheld_info = {
                "id": f"{field_identifier[0]}-{lot_result_id[0]}",
                "field": "buy-rev-cou",
                "name": "buyer Review Request Count",
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt635_unpublished_identifier(release_json, unpublished_identifier_data):
    """
    Merge the parsed unpublished identifier data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-635)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_identifier_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item.update(new_item)
        else:
            withheld_info.append(new_item)

    logger.info(
        "Merged %d unpublished identifier(s) for BT-195(BT-635)",
        len(unpublished_identifier_data["withheldInformation"]),
    )
