"""TED BT-09 Cross Border Law converter.

Maps the applicable law description for cross-border procurement procedures
from PROCUREMENT_LAW elements to OCDS tender.crossBorderLaw field.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# TED form types that may contain cross border law information
TED_FORM_TYPES = [
    "F01_2014",
    "F02_2014",
    "F03_2014",
    "F04_2014",
    "F05_2014",
    "F12_2014",
    "F13_2014",
    "F21_2014",
    "F22_2014",
]


def parse_cross_border_law(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse the cross border law description (BT-09) from TED XML content.

    Extracts the PROCUREMENT_LAW element from various TED form types and
    maps it to the OCDS tender.crossBorderLaw field.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing cross border law mapping like:
        {'tender': {'crossBorderLaw': '<law description>'}}
        or None if not found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Invalid XML content provided")
        return None

    law_text = None

    # Try each form type path to find the procurement law
    for form_type in TED_FORM_TYPES:
        xpath = (
            f"//TED_EXPORT/FORM_SECTION/{form_type}/CONTRACTING_BODY/PROCUREMENT_LAW"
        )
        law_elements = root.xpath(xpath)

        if law_elements and law_elements[0].text:
            law_text = law_elements[0].text.strip()
            logger.info("Found Cross Border Law (BT-09) in form type %s", form_type)
            break

    if not law_text:
        logger.warning("No Cross Border Law (BT-09) found in any form type")
        return None

    return {"tender": {"crossBorderLaw": law_text}}


def merge_cross_border_law(
    release_json: dict[str, Any], cross_border_law_data: dict[str, Any] | None
) -> None:
    """Merge cross border law data into the release JSON.

    Updates the tender.crossBorderLaw field with the law description.

    Args:
        release_json: The target release JSON to update
        cross_border_law_data: The cross border law data to merge
    """
    if cross_border_law_data and "tender" in cross_border_law_data:
        release_json.setdefault("tender", {})
        release_json["tender"]["crossBorderLaw"] = cross_border_law_data["tender"][
            "crossBorderLaw"
        ]
        logger.info("Merged Cross Border Law (BT-09) into the release JSON")
    else:
        logger.warning("No Cross Border Law (BT-09) data to merge")
