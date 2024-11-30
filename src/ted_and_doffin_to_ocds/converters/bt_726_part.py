# converters/bt_726_part.py

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


def parse_part_sme_suitability(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse BT-726-Part: The buyer emphasizes that this procurement part is suitable for SMEs.

    Args:
        xml_content: XML content to parse

    Returns:
        Dictionary containing SME suitability or None if not found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        sme_suitable = root.xpath(
            "string(/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
            "/cac:ProcurementProject/cbc:SMESuitableIndicator)",
            namespaces=NAMESPACES,
        )

        if sme_suitable:
            is_suitable = sme_suitable.lower() == "true"
            logger.info("Found part SME suitability: %s", is_suitable)
            return {"tender": {"suitability": {"sme": is_suitable}}}

        logger.debug("No SME suitability indicator found")
        return None  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise


def merge_part_sme_suitability(
    release_json: dict[str, Any], part_sme_data: dict[str, Any] | None
) -> None:
    """
    Merge SME suitability data into release JSON.

    Args:
        release_json: Target release JSON to update
        part_sme_data: SME suitability data to merge
    """
    if not part_sme_data:
        logger.debug("No SME suitability data to merge")
        return

    tender = release_json.setdefault("tender", {})
    suitability = tender.setdefault("suitability", {})
    suitability["sme"] = part_sme_data["tender"]["suitability"]["sme"]
    logger.info("Merged SME suitability: %s", suitability["sme"])
