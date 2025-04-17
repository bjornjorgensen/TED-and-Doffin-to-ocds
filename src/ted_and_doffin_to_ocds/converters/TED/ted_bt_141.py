import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-141: Change Description
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F20_2014/MODIFICATIONS_CONTRACT/INFO_MODIFICATIONS/SHORT_DESCR
# OCDS Mapping: tender.amendments[].description


def parse_change_description(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse the change description from TED XML.

    Args:
        xml_content: The TED XML content as string or bytes.

    Returns:
        A dictionary containing tender.amendments with descriptions,
        or None if not found.
        Example: {"tender": {"amendments": [{"description": "The changes have been applied to..."}]}}
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)

        # XPath for F20_2014 forms
        xpath = "FORM_SECTION/F20_2014/MODIFICATIONS_CONTRACT/INFO_MODIFICATIONS/SHORT_DESCR/text()"
        descriptions = root.xpath(xpath)

        if descriptions:
            amendments = [
                {"description": desc.strip()}
                for desc in descriptions
                if desc and desc.strip()
            ]

            if amendments:
                return {"tender": {"amendments": amendments}}
    except Exception as e:
        logger.warning("Error parsing change description: %s", e)

    return None


def merge_change_description(
    release_json: dict[str, Any], parsed_data: dict[str, Any] | None
) -> None:
    """
    Merge the parsed change description into the release JSON.

    Args:
        release_json: The release JSON to merge into.
        parsed_data: The parsed data dictionary from parse_change_description.
    """
    if (
        not parsed_data
        or "tender" not in parsed_data
        or "amendments" not in parsed_data["tender"]
    ):
        logger.info("No change description data to merge.")
        return

    tender = release_json.setdefault("tender", {})
    amendments = tender.setdefault("amendments", [])

    # If there are existing amendments, update them with descriptions
    # Otherwise, add the new amendments
    if amendments and parsed_data["tender"]["amendments"]:
        for i, new_amendment in enumerate(parsed_data["tender"]["amendments"]):
            if i < len(amendments):
                # Update existing amendment
                if "description" in new_amendment:
                    amendments[i]["description"] = new_amendment["description"]
            else:
                # Add new amendment
                amendments.append(new_amendment)
    else:
        # No existing amendments, add all new ones
        amendments.extend(parsed_data["tender"]["amendments"])

    logger.info(
        "Merged %d change descriptions.", len(parsed_data["tender"]["amendments"])
    )
