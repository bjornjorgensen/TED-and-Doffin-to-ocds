# converters/bt_5121_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_place_performance_post_code_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse place performance postal code (BT-5121) from XML content.

    Gets postal code information for each part's delivery address. Creates/updates
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

        parts = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
            namespaces=NAMESPACES,
        )

        found_postal_codes = False
        for part in parts:
            try:
                postal_zones = part.xpath(
                    "cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:PostalZone/text()",
                    namespaces=NAMESPACES,
                )

                for postal_zone in postal_zones:
                    if postal_zone.strip():
                        found_postal_codes = True
                        result["tender"]["deliveryAddresses"].append(
                            {"postalCode": postal_zone.strip()}
                        )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete part data: %s", e)
                continue

        if found_postal_codes:
            return result

    except Exception:
        logger.exception("Error parsing place performance post code")
        return None
    else:
        return None


def merge_place_performance_post_code_part(
    release_json: dict[str, Any], post_code_data: dict[str, Any] | None
) -> None:
    """Merge postal code data into the release JSON.

    Updates the tender.deliveryAddresses array in release_json with new postal codes,
    preserving existing address data while adding/updating postal codes.

    Args:
        release_json: The target release JSON to update
        post_code_data: The source data containing postal codes to merge

    Returns:
        None

    """
    if not post_code_data:
        logger.warning("No Place Performance Post Code (part) data to merge")
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in post_code_data["tender"]["deliveryAddresses"]:
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

    logger.info(
        "Merged Place Performance Post Code (part) data for %d addresses",
        len(post_code_data["tender"]["deliveryAddresses"]),
    )
