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
        }

        result = {"awards": []}

        privacies = root.xpath("//efac:FieldsPrivacy", namespaces=namespaces)

        for privacy in privacies:
            try:
                reasons = privacy.xpath(
                    "efbc:ReasonDescription/text()", namespaces=namespaces
                )
                if not reasons:
                    logger.debug("No reason description found in privacy element")
                    continue

                reason = reasons[0]
                reason_codes = privacy.xpath(
                    "efbc:ReasonCode/text()", namespaces=namespaces
                )
                if not reason_codes:
                    logger.debug(
                        "No reason code found for privacy element with reason: %s",
                        reason,
                    )
                    continue

                result["awards"].append(
                    {
                        "id": str(len(result["awards"]) + 1),
                        "justification": {"description": reason, "id": reason_codes[0]},
                    }
                )

            except (IndexError, AttributeError) as e:
                logger.warning("Error processing privacy element: %s", e)
                continue

        return result if result["awards"] else None

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
            existing_item["rationale"] = new_item["rationale"]
        else:
            withheld_info.append(new_item)

    logger.info("Merged unpublished justification data for BT-196(BT-142)")
