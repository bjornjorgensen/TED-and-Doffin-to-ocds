# converters/bt_728_Lot.py

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


def parse_lot_place_performance_additional(
    xml_content: str | bytes,
) -> dict | None:
    """Parse additional place of performance information for lots (BT-728)."""
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"items": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
                descriptions = lot.xpath(
                    "./cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()",
                    namespaces=NAMESPACES,
                )

                if descriptions:
                    # Concatenate all descriptions into a single deliveryLocation object
                    # instead of creating a separate entry for each description
                    concatenated_description = " ".join(
                        desc.strip() for desc in descriptions if desc.strip()
                    )

                    if concatenated_description:
                        item = {
                            "id": str(len(result["tender"]["items"]) + 1),
                            "relatedLot": lot_id,
                            "deliveryLocations": [
                                {"description": concatenated_description}
                            ],
                        }
                        result["tender"]["items"].append(item)

            except IndexError:
                logger.warning("Missing required data for lot in BT-728")
                continue

        return result if result["tender"]["items"] else None

    except Exception:
        logger.exception("Error processing BT-728 lot data")
        return None


def merge_lot_place_performance_additional(
    release_json: dict[str, Any],
    lot_place_performance_additional_data: dict[str, Any] | None,
) -> None:
    """Merge additional place performance data into release JSON."""
    if not lot_place_performance_additional_data:
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in lot_place_performance_additional_data["tender"]["items"]:
        try:
            existing_item = next(
                (
                    item
                    for item in existing_items
                    if item.get("relatedLot") == new_item["relatedLot"]
                ),
                None,
            )

            if existing_item:
                existing_locations = existing_item.setdefault("deliveryLocations", [])
                for new_location in new_item["deliveryLocations"]:
                    if new_location not in existing_locations:
                        existing_locations.append(new_location)
            else:
                existing_items.append(new_item)

        except Exception:
            logger.exception("Error merging delivery location for lot")
            continue
