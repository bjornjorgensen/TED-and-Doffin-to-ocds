# converters/bt_196_bt_142_LotResult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt196_bt142_unpublished_justification(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse unpublished justification data from XML content."""
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        namespaces = {
            "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
            "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
            "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
            "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        }

        result = {"withheldInformation": []}

        # Use the specific XPath for BT-196(BT-142)-LotResult
        privacies = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-cho']",
            namespaces=namespaces,
        )

        for privacy in privacies:
            try:
                # Get ReasonDescription elements to handle multilingual text
                reason_elements = privacy.xpath(
                    "efbc:ReasonDescription", namespaces=namespaces
                )
                if not reason_elements:
                    logger.debug("No reason description found in privacy element")
                    continue

                # Process all language variants
                multilingual_reasons = []
                for reason_element in reason_elements:
                    text = reason_element.text
                    language_id = reason_element.get("languageID")

                    if text:
                        reason_obj = {"text": text}
                        if language_id:
                            reason_obj["languageID"] = language_id
                        multilingual_reasons.append(reason_obj)

                if not multilingual_reasons:
                    logger.debug("No valid reason text found in privacy element")
                    continue

                reason_codes = privacy.xpath(
                    "efbc:ReasonCode/text()", namespaces=namespaces
                )
                if not reason_codes:
                    logger.debug(
                        "No reason code found for privacy element with reason",
                    )
                    continue

                # Use the first language variant as the primary rationale
                # but store all language variants in the result
                primary_reason = multilingual_reasons[0]["text"]

                result["withheldInformation"].append(
                    {
                        "id": str(len(result["withheldInformation"]) + 1),
                        "rationale": primary_reason,
                        "rationaleMultilingual": multilingual_reasons,
                    }
                )

            except (IndexError, AttributeError) as e:
                logger.warning("Error processing privacy element: %s", e)
                continue

        return result if result["withheldInformation"] else None

    except Exception:
        logger.exception("Error parsing unpublished justification data")
        return None


def merge_bt196_bt142_unpublished_justification(
    release_json: dict,
    unpublished_justification_data: dict | None,
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
        logger.warning("No unpublished justification data to merge for BT-196(BT-142)")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_justification_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            # Add the new rationale fields to the existing item structure
            existing_item["rationale"] = new_item["rationale"]
            # Also include multilingual rationales if available
            if "rationaleMultilingual" in new_item:
                existing_item["rationaleMultilingual"] = new_item["rationaleMultilingual"]
        else:
            # If creating a new item, we need to handle that field and name might be expected
            # but our parser doesn't generate them
            if "field" not in new_item and "id" in new_item and new_item["id"].startswith("win-cho"):
                new_item["field"] = "win-cho"
                new_item["name"] = "Winner Chosen"
            withheld_info.append(new_item)

    logger.info("Merged unpublished justification data for BT-196(BT-142)")
