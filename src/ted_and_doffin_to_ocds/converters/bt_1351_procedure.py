# converters/bt_1351_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_accelerated_procedure_justification(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the accelerated procedure justification (BT-1351) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed accelerated procedure data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "procedure": {
                    "acceleratedRationale": "..."
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

    xpath = "/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/cbc:ProcessReason"
    process_reason = root.xpath(xpath, namespaces=namespaces)

    if process_reason:
        return {
            "tender": {"procedure": {"acceleratedRationale": process_reason[0].text}},
        }
    logger.info("No accelerated procedure justification found")
    return None


def merge_accelerated_procedure_justification(
    release_json: dict[str, Any],
    accelerated_data: dict[str, Any] | None,
) -> None:
    """Merge accelerated procedure justification data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        accelerated_data: The accelerated procedure data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not accelerated_data:
        logger.warning("No accelerated procedure justification data to merge")
        return

    tender = release_json.setdefault("tender", {})
    procedure = tender.setdefault("procedure", {})
    procedure.update(accelerated_data["tender"]["procedure"])
    logger.info("Merged accelerated procedure justification data")
