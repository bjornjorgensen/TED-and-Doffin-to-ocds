# converters/bt_538_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_duration_other(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the duration description (BT-538) for procurement project parts from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed part duration description data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "contractPeriod": {
                    "description": "UNLIMITED"
                }
            }
        }
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

    result = {"tender": {}}

    duration_code = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:ProcurementProject/cac:PlannedPeriod/cbc:DescriptionCode[@listName='timeperiod']/text()",
        namespaces=namespaces,
    )

    if duration_code:
        result["tender"]["contractPeriod"] = {"description": duration_code[0]}

    return result if result["tender"] else None


def merge_part_duration_other(
    release_json: dict[str, Any], part_duration_other_data: dict[str, Any] | None
) -> None:
    """Merge part duration description data into the main release JSON.

    Args:
        release_json: The main release JSON to merge data into
        part_duration_other_data: The part duration description data to merge from

    Returns:
        None - modifies release_json in place
    """
    if not part_duration_other_data:
        logger.warning("No part Duration Other data to merge")
        return

    tender = release_json.setdefault("tender", {})

    if "contractPeriod" in part_duration_other_data["tender"]:
        tender.setdefault("contractPeriod", {}).update(
            part_duration_other_data["tender"]["contractPeriod"],
        )
        logger.info("Merged part Duration Other data")
    else:
        logger.info("No part Duration Other data to merge")
