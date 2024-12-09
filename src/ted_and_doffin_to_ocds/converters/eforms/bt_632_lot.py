# converters/bt_632_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tool_name(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the tool name (BT-632) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed tool name data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "LOT-0001",
                        "communication": {
                            "atypicalToolName": "AbcKomSoft"
                        }
                    }
                ]
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

    result = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        tool_name = lot.xpath(
            "cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efbc:AccessToolName/text()",
            namespaces=namespaces,
        )

        if tool_name:
            lot_data = {
                "id": lot_id,
                "communication": {"atypicalToolName": tool_name[0]},
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_tool_name(
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
        logger.warning("No tool name data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in tool_name_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("communication", {}).update(
                new_lot["communication"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged tool name data for %d lots", len(tool_name_data["tender"]["lots"])
    )
