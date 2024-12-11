# converters/bt_632_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tool_name_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the tool name (BT-632) for procurement project parts from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed tool name data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "communication": {
                    "atypicalToolName": "AbcKomSoft"
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

    tool_name = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:AccessToolName/text()",
        namespaces=namespaces,
    )

    if tool_name:
        return {"tender": {"communication": {"atypicalToolName": tool_name[0]}}}

    return None


def merge_tool_name_part(
    release_json: dict[str, Any],
    tool_name_data: dict[str, Any] | None,
) -> None:
    """Merge tool name data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        tool_name_data: The tool name data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not tool_name_data:
        logger.warning("No tool name data to merge for part")
        return

    release_json.setdefault("tender", {}).setdefault("communication", {}).update(
        tool_name_data["tender"]["communication"],
    )

    logger.info("Merged tool name data for part")
