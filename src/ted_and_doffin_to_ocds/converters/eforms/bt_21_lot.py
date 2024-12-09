# converters/bt_21_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_title(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse lot titles from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing lots data with titles,
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
        lot_title = lot.xpath(
            "cac:ProcurementProject/cbc:Name/text()",
            namespaces=namespaces,
        )

        if lot_title:
            result["tender"]["lots"].append({"id": lot_id, "title": lot_title[0]})

    return result if result["tender"]["lots"] else None


def merge_lot_title(
    release_json: dict[str, Any], lot_title_data: dict[str, Any] | None
) -> None:
    """Merge lot title data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        lot_title_data (Optional[Dict[str, Any]]): Lot data containing titles to merge

    """
    if not lot_title_data:
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in lot_title_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["title"] = new_lot["title"]
        else:
            existing_lots.append(new_lot)
