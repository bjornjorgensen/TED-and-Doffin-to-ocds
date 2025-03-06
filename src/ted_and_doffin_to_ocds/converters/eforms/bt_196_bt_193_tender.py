# converters/bt_196_bt_193_Tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt196_bt193_unpublished_justification(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the XML content to extract winning tender variant unpublished justification.

    Processes XML content to find unpublished justification related to tender variant
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
                        "rationale": str
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    # Use the provided absolute XPath to directly locate the ReasonDescription elements
    xpath_reason_descriptions = (
        "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent"
        "/efext:EformsExtension/efac:NoticeResult/efac:LotTender"
        "/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-ten-var']/efbc:ReasonDescription"
    )

    result = {"withheldInformation": []}
    reason_elements = root.xpath(xpath_reason_descriptions, namespaces=namespaces)

    for reason_element in reason_elements:
        # Get the parent FieldsPrivacy element
        privacy = reason_element.getparent()

        tender_id = privacy.xpath(
            "ancestor::efac:LotTender/cbc:ID/text()", namespaces=namespaces
        )[0]
        reason = reason_element.text
        field_id = "win-ten-var"

        withheld_info = {
            "id": f"{field_id}-{tender_id}",
            "field": field_id,
            "rationale": reason,
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt196_bt193_unpublished_justification(
    release_json: dict, unpublished_justification_data: dict | None
) -> None:
    """Merge the parsed unpublished justification data into the main OCDS release JSON.

    Takes the unpublished justification data and merges it into the main OCDS release JSON
    by updating withheld information items with matching IDs.

    Args:
        release_json: The main OCDS release JSON to be updated.
        unpublished_justification_data: The parsed unpublished justification data to be merged.
            Should contain a 'withheldInformation' list of dictionaries with rationale.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not unpublished_justification_data:
        logger.warning("No unpublished justification data to merge for BT-196(BT-193)")
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
        "Merged unpublished justification data for BT-196(BT-193): %d items",
        len(unpublished_justification_data["withheldInformation"]),
    )
