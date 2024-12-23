# converters/bt_5121_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_post_code(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse place performance postal code (BT-5121) from XML content.

    Gets postal code information for each lot's delivery address. Creates/updates
    corresponding Address objects in the item's deliveryAddresses array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing tender items with delivery addresses or None if no data found

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

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        postal_zones = lot.xpath(
            "cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:PostalZone/text()",
            namespaces=namespaces,
        )

        if postal_zones:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "deliveryAddresses": [
                    {"postalCode": postal_zone} for postal_zone in postal_zones
                ],
                "relatedLot": lot_id,
            }
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_place_performance_post_code(
    release_json: dict[str, Any], post_code_data: dict[str, Any] | None
) -> None:
    """Merge postal code data into the release JSON."""
    if not post_code_data:
        logger.warning("No Place Performance Post Code data to merge")
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in post_code_data["tender"]["items"]:
        if "relatedLot" not in new_item:
            logger.warning("Skipping item without relatedLot: %s", new_item)
            continue

        try:
            existing_item = next(
                (
                    item
                    for item in existing_items
                    if "relatedLot" in item
                    and item["relatedLot"] == new_item["relatedLot"]
                ),
                None,
            )

            if existing_item:
                existing_addresses = existing_item.setdefault("deliveryAddresses", [])
                for new_address in new_item["deliveryAddresses"]:
                    matching_address = next(
                        (
                            addr
                            for addr in existing_addresses
                            if addr.get("postalCode") == new_address["postalCode"]
                        ),
                        None,
                    )
                    if matching_address:
                        matching_address.update(new_address)
                    else:
                        existing_addresses.append(new_address)
            else:
                existing_items.append(new_item)

        except KeyError as e:
            logger.warning("Error accessing relatedLot: %s", e)
            continue

    logger.info(
        "Merged Place Performance Post Code data for %d items",
        len(post_code_data["tender"]["items"]),
    )
