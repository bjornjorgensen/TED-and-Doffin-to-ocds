"""
BT-09 Cross Border Law converter.

Maps the applicable law description for cross-border procurement procedures
from DocumentDescription to OCDS tender.crossBorderLaw field.
"""

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_cross_border_law(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse the cross border law description (BT-09) from XML content.

    Extracts the DocumentDescription text from ProcurementLegislationDocumentReference
    where ID is 'CrossBorderLaw'.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        Dictionary containing cross border law mapping like:
        {'tender': {'crossBorderLaw': '<law description>'}}
        or None if not found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    xpath = "//cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/cbc:DocumentDescription/text()"
    cross_border_law = root.xpath(xpath, namespaces=NAMESPACES)

    if cross_border_law:
        return {"tender": {"crossBorderLaw": cross_border_law[0]}}
    logger.warning("No Cross Border Law (BT-09) found in the XML")
    return None


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
