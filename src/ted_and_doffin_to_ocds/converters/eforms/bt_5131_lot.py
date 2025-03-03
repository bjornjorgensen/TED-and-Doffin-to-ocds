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
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
                cities = lot.xpath(
                    "./cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CityName/text()",
                    namespaces=NAMESPACES,
                )

                if cities:
                    filtered_cities = [city.strip() for city in cities if city.strip()]
                    if filtered_cities:
                        item = {
                            "id": lot_id,
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


def _ensure_tender_items_exist(release_json: dict[str, Any]) -> None:
    """Ensure tender and items exist in the release JSON."""
    if "tender" not in release_json:
        release_json["tender"] = {}

    if "items" not in release_json["tender"]:
        release_json["tender"]["items"] = []


def _merge_delivery_addresses(
    existing_item: dict[str, Any], new_item: dict[str, Any]
) -> None:
    """Merge delivery addresses from new_item into existing_item."""
    if "deliveryAddresses" not in existing_item:
        existing_item["deliveryAddresses"] = new_item["deliveryAddresses"]
        return

    for address in new_item["deliveryAddresses"]:
        existing_addr_found = False
        for existing_addr in existing_item["deliveryAddresses"]:
            if "locality" not in existing_addr:
                existing_addr["locality"] = address["locality"]
                existing_addr_found = True
                break

        if not existing_addr_found:
            existing_item["deliveryAddresses"].append(address)


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
    if not place_performance_city_data or not place_performance_city_data.get(
        "tender", {}
    ).get("items"):
        logger.warning("No Place Performance City data to merge")
        return

    _ensure_tender_items_exist(release_json)

    for new_item in place_performance_city_data["tender"]["items"]:
        try:
            existing_item = next(
                (
                    item
                    for item in release_json["tender"]["items"]
                    if item.get("id") == new_item.get("id")
                ),
                None,
            )

            if existing_item:
                _merge_delivery_addresses(existing_item, new_item)
            else:
                release_json["tender"]["items"].append(new_item)

        except Exception:
            logger.exception("Error processing BT-5131 (Place Performance City) data")
            raise

    logger.info(
        "Merged Place Performance City data for %d items",
        len(place_performance_city_data["tender"]["items"]),
    )
