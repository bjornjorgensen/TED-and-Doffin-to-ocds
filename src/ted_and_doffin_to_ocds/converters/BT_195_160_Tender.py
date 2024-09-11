# converters/BT_195_160_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def bt_195_bt_160_parse_unpublished_identifier(xml_content):
    """
    Parse the XML content to extract the unpublished identifier information for BT-195 and BT-160.

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

    xpath_query = "//efac:NoticeResult/efac:LotTender/efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='con-rev-buy']"
    field_privacy_elements = root.xpath(xpath_query, namespaces=namespaces)

    for element in field_privacy_elements:
        lot_tender_id = element.xpath(
            "ancestor::efac:LotTender/cbc:ID/text()", namespaces=namespaces
        )
        if lot_tender_id:
            withheld_item = {
                "id": f"con-rev-buy-{lot_tender_id[0]}",
                "field": "con-rev-buy",
                "name": "Concession Revenue Buyer",
            }
            result["withheldInformation"].append(withheld_item)

    return result if result["withheldInformation"] else None


def bt_195_bt_160_merge_unpublished_identifier(
    release_json, unpublished_identifier_data
):
    """
    Merge the parsed unpublished identifier data for BT-195 and BT-160 into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_identifier_data (dict): The parsed unpublished identifier data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge for BT-195 and BT-160")
        return

    withheld_information = release_json.setdefault("withheldInformation", [])
    withheld_information.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        f"Merged unpublished identifier data for BT-195 and BT-160: {len(unpublished_identifier_data['withheldInformation'])} items"
    )
