# converters/bt_196_bt_160_Tender.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt196_bt160_unpublished_justification(xml_content):
    """
    Parse the XML content to extract the unpublished justification description for the concession revenue buyer.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished justification data.
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

    lot_tenders = root.xpath(
        "//efac:noticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        lot_tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)
        reason_description = lot_tender.xpath(
            "efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='con-rev-buy']/efbc:ReasonDescription/text()",
            namespaces=namespaces,
        )

        if lot_tender_id and reason_description:
            withheld_info = {
                "id": f"con-rev-buy-{lot_tender_id[0]}",
                "field": "con-rev-buy",
                "rationale": reason_description[0],
            }
            result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt196_bt160_unpublished_justification(
    release_json,
    unpublished_justification_data,
):
    """
    Merge the parsed unpublished justification data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_justification_data (dict): The parsed unpublished justification data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not unpublished_justification_data:
        logger.warning("No unpublished justification data to merge for BT-196(BT-160)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_justification_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item["rationale"] = new_item["rationale"]
        else:
            withheld_info.append(new_item)

    logger.info(
        "Merged unpublished justification data for BT-196(BT-160): %d items",
        len(unpublished_justification_data["withheldInformation"]),
    )