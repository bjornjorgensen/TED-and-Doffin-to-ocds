import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_place_performance_city_procedure(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse place performance city (BT-5131) from XML content.

    Gets city information for each delivery address. Creates/updates
    corresponding Address objects in the tender.deliveryAddresses array.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing tender delivery addresses or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"deliveryAddresses": []}}

        cities = root.xpath(
            "//cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CityName/text()",
            namespaces=NAMESPACES,
        )

        for city in cities:
            if city.strip():
                result["tender"]["deliveryAddresses"].append({"locality": city.strip()})

        if result["tender"]["deliveryAddresses"]:
            return result

    except Exception:
        logger.exception("Error parsing place performance city")
        return None

    return None


def merge_place_performance_city_procedure(
    release_json: dict[str, Any],
    place_performance_city_data: dict[str, Any] | None,
) -> None:
    """
    Merge city data into the release JSON.

    Updates the tender.deliveryAddresses array in release_json with new cities,
    preserving existing address data while adding/updating localities.

    Args:
        release_json: The target release JSON to update
        place_performance_city_data: The source data containing cities to merge

    Returns:
        None
    """
    if not place_performance_city_data:
        logger.warning("No Place Performance City procedure data to merge")
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in place_performance_city_data["tender"]["deliveryAddresses"]:
        matching_address = next(
            (
                addr
                for addr in existing_addresses
                if addr.get("locality") == new_address["locality"]
            ),
            None,
        )
        if matching_address:
            matching_address.update(new_address)
        else:
            existing_addresses.append(new_address)

    logger.info(
        "Merged Place Performance City procedure data for %d addresses",
        len(place_performance_city_data["tender"]["deliveryAddresses"]),
    )
