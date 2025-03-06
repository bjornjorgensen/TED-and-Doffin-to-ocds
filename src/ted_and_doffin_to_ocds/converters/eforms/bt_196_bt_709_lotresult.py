# converters/bt_196_bt_709_LotResult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt196_bt709_unpublished_justification(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the XML content to extract the unpublished justification description for the maximum value.

    This function extracts BT-196 (justification) data related to BT-709 (LotResult) from the XML.
    It looks for FieldsPrivacy elements containing reasons why certain framework agreement value information is withheld.

    Args:
        xml_content: The XML content to parse, either as a string or bytes object.
            Must be valid XML containing eForms namespaces and lot result data.

    Returns:
        Optional[Dict]: A dictionary containing the parsed unpublished justification data in the format:
            {
                "withheldInformation": [
                    {
                        "id": "max-val-{lot_result_id}",
                        "rationale": "Justification text"
                    },
                    ...
                ]
            }
        Returns None if no relevant data is found or if XML parsing fails.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"withheldInformation": []}

    # Use the absolute XPath to get all ReasonDescription elements
    xpath_query = "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FrameworkAgreementValues/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='max-val']/efbc:ReasonDescription"

    reason_descriptions = root.xpath(xpath_query, namespaces=namespaces)

    for reason_desc in reason_descriptions:
        # Get the LotResult ID by traversing back up the tree
        lot_result = reason_desc.xpath(
            "ancestor::efac:LotResult",
            namespaces=namespaces,
        )[0]
        lot_result_id = lot_result.xpath("cbc:ID/text()", namespaces=namespaces)[0]

        # Get the reason description text
        reason_text = reason_desc.text

        if reason_text:
            withheld_info = {
                "id": f"max-val-{lot_result_id}",
                "rationale": reason_text,
            }
            result["withheldInformation"].append(withheld_info)

    if not result["withheldInformation"]:
        logger.debug(
            "No unpublished justification data found for BT-196(BT-709) LotResult"
        )
        return None

    return result


def merge_bt196_bt709_unpublished_justification(
    release_json: dict,
    unpublished_justification_data: dict | None,
) -> None:
    """Merge the parsed unpublished justification data into the main OCDS release JSON.

    This function updates the withheldInformation array in the release_json with justification
    data from unpublished fields related to lot result maximum values.

    Args:
        release_json: The main OCDS release JSON document to be updated.
            Must be a mutable dictionary that may contain a withheldInformation array.
        unpublished_justification_data: The parsed unpublished justification data to be merged.
            Should contain a withheldInformation array with objects having id and rationale fields.
            Can be None, in which case no changes are made.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not unpublished_justification_data:
        logger.warning(
            "No unpublished justification data to merge for BT-196(BT-709) LotResult",
        )
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
        "Merged unpublished justification data for BT-196(BT-709) LotResult for %d lot results",
        len(unpublished_justification_data["withheldInformation"]),
    )
