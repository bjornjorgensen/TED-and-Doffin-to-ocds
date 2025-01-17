# converters/bt_538_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_duration_other(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the duration description (BT-538) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed lot duration description data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "lot-id",
                        "contractPeriod": {
                            "description": "UNLIMITED"
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
        duration_code = lot.xpath(
            "cac:ProcurementProject/cac:PlannedPeriod/cbc:DescriptionCode[@listName='timeperiod']/text()",
            namespaces=namespaces,
        )

        if duration_code:
            result["tender"]["lots"].append(
                {"id": lot_id, "contractPeriod": {"description": duration_code[0]}},
            )

    return result if result["tender"]["lots"] else None


def merge_lot_duration_other(
    release_json: dict[str, Any], lot_duration_other_data: dict[str, Any] | None
) -> None:
    """Merge lot duration description data into the main release JSON.

    Args:
        release_json: The main release JSON to merge data into
        lot_duration_other_data: The lot duration description data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not lot_duration_other_data:
        logger.warning("No Lot Duration Other data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_duration_other_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("contractPeriod", {}).update(
                new_lot["contractPeriod"],
            )
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Lot Duration Other data for %s lots",
        len(lot_duration_other_data["tender"]["lots"]),
    )
