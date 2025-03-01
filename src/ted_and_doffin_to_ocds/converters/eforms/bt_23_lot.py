# converters/bt_23_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_main_nature(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse main procurement nature for each lot from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing lots data with main procurement categories,
                                 or None if no valid data is found

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
        procurement_type = lot.xpath(
            "cac:ProcurementProject/cbc:ProcurementTypeCode[@listName='contract-nature']/text()",
            namespaces=namespaces,
        )

        if procurement_type:
            main_category = procurement_type[0]
            if main_category == "supplies":
                main_category = "goods"

            result["tender"]["lots"].append(
                {"id": lot_id, "mainProcurementCategory": main_category},
            )

    return result if result["tender"]["lots"] else None


def merge_main_nature(
    release_json: dict[str, Any], main_nature_data: dict[str, Any] | None
) -> None:
    """Merge main procurement nature data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        main_nature_data (Optional[Dict[str, Any]]): Lot data containing main procurement categories to merge

    """
    if not main_nature_data:
        logger.warning("No Main Nature data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in main_nature_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["mainProcurementCategory"] = new_lot["mainProcurementCategory"]
        else:
            tender_lots.append(new_lot)

    logger.info(
        "Merged Main Nature data for %d lots",
        len(main_nature_data["tender"]["lots"]),
    )
