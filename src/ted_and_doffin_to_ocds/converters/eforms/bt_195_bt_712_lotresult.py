# converters/bt_195_bt_712_LotResult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt195_bt712_unpublished_identifier(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the XML content to extract buyer review complainants unpublished identifier.

    Processes XML content to find unpublished identifiers related to appeal requests statistics
    and creates a structured dictionary containing withheld information.

    Args:
        xml_content: The XML content to parse, either as string or bytes.

    Returns:
        Optional[Dict]: A dictionary containing withheld information with structure:
            {
                "withheldInformation": [
                    {
                        "id": str,
                        "field": str,
                        "name": str
                    }
                ]
            }
        Returns None if no relevant data is found.

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

    xpath_query = (
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
        "/efext:EformsExtension/efac:NoticeResult/efac:LotResult"
        "/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']"
        "/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='rev-req']"
        "/efbc:FieldIdentifierCode"
    )

    field_identifier_codes = root.xpath(xpath_query, namespaces=namespaces)

    for field_identifier_code in field_identifier_codes:
        lot_result_id = field_identifier_code.xpath(
            "ancestor::efac:LotResult/cbc:ID/text()",
            namespaces=namespaces,
        )[0]

        withheld_info = {
            "id": f"{field_identifier_code.text}-{lot_result_id}",
            "field": "rev-req",
            "name": "Buyer Review Complainants",
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt195_bt712_unpublished_identifier(
    release_json: dict, unpublished_identifier_data: dict | None
) -> None:
    """Merge the parsed unpublished identifier data into the main OCDS release JSON.

    Takes the unpublished identifier data and merges it into the main OCDS release JSON
    by appending withheld information items to the release's withheldInformation array.

    Args:
        release_json: The main OCDS release JSON to be updated.
        unpublished_identifier_data: The parsed unpublished identifier data to be merged.
            Should contain a 'withheldInformation' list of dictionaries.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not unpublished_identifier_data:
        logger.warning("No unpublished identifier data to merge for BT-195(BT-712)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])
    withheld_info.extend(unpublished_identifier_data["withheldInformation"])

    logger.info(
        "Merged %d unpublished identifier(s) for BT-195(BT-712)",
        len(unpublished_identifier_data["withheldInformation"]),
    )