# converters/bt_531_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_additional_nature(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the additional nature (BT-531) for procurement project lots from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed lot additional nature data in OCDS format, or None if no data found.
        Format:
        {
            "tender": {
                "lots": [
                    {
                        "id": "lot-id",
                        "additionalProcurementCategories": ["nature1", "nature2"]
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
        additional_natures = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='contract-nature']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces,
        )

        if additional_natures:
            lot_data = {
                "id": lot_id,
                "additionalProcurementCategories": additional_natures,
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_lot_additional_nature(
    release_json: dict[str, Any], lot_additional_nature_data: dict[str, Any] | None
) -> None:
    """Merge lot additional nature data into the main release JSON.

    Args:
        release_json: The main release JSON to merge data into
        lot_additional_nature_data: The lot additional nature data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not lot_additional_nature_data:
        logger.warning("No Lot Additional Nature data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in lot_additional_nature_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["additionalProcurementCategories"] = new_lot[
                "additionalProcurementCategories"
            ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Lot Additional Nature data for %s lots",
        len(lot_additional_nature_data["tender"]["lots"]),
    )
