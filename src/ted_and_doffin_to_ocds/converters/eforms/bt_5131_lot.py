# converters/bt_5131_Lot.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_place_performance_city(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse place performance city (BT-5131) from XML content.

    Gets city information for each lot's delivery address. Creates/updates
    corresponding Address objects in the item's deliveryAddresses array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing tender items with delivery addresses or None if no data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"items": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
                cities = lot.xpath(
                    ".//cac:RealizedLocation/cac:Address/cbc:CityName/text()",
                    namespaces=NAMESPACES,
                )

                if cities:
                    filtered_cities = [city.strip() for city in cities if city.strip()]
                    if filtered_cities:
                        item = {
                            "id": str(len(result["tender"]["items"]) + 1),
                            "relatedLot": lot_id,
                            "deliveryAddresses": [
                                {"locality": city} for city in filtered_cities
                            ],
                        }
                        result["tender"]["items"].append(item)

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot data: %s", e)
                continue

        if result["tender"]["items"]:
            return result

    except Exception:
        logger.exception("Error parsing place performance city")
        return None

    return None


def merge_place_performance_city(
    release_json: dict[str, Any], place_performance_city_data: dict[str, Any] | None
) -> None:
    """Merge city data into the release JSON.

    Updates or creates delivery addresses with locality information for each lot.
    Preserves existing address data while adding/updating cities.

    Args:
        release_json: The target release JSON to update
        place_performance_city_data: The source data containing cities to merge

    Returns:
        None

    """
    if not place_performance_city_data:
        logger.warning("No Place Performance City data to merge")
        return

    tender_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in place_performance_city_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in tender_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )

        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            for new_address in new_item["deliveryAddresses"]:
                if existing_addresses:
                    existing_addresses[0].update(new_address)
                else:
                    existing_addresses.append(new_address)
        else:
            tender_items.append(new_item)

    logger.info(
        "Merged Place Performance City data for %d items",
        len(place_performance_city_data["tender"]["items"]),
    )