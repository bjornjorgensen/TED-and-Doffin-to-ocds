import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_procedure_place_performance_street(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse procedure place performance street (BT-5101(a)) from XML content."""
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"deliveryAddresses": []}}

        # Get all locations using exact BT-5101 path
        realized_locations = root.xpath(
            "/*/cac:ProcurementProject/cac:RealizedLocation", namespaces=NAMESPACES
        )

        found_addresses = False
        for location in realized_locations:
            address_parts = []

            # Get street name
            street_name = location.xpath(
                "cac:Address/cbc:StreetName/text()", namespaces=NAMESPACES
            )
            if street_name:
                address_parts.append(street_name[0])

            # Get additional street name
            additional_street = location.xpath(
                "cac:Address/cbc:AdditionalStreetName/text()", namespaces=NAMESPACES
            )
            if additional_street:
                address_parts.append(additional_street[0])

            # Get address lines
            address_lines = location.xpath(
                "cac:Address/cac:AddressLine/cbc:Line/text()", namespaces=NAMESPACES
            )
            address_parts.extend(address_lines)

            if address_parts:
                found_addresses = True
                street_address = ", ".join(
                    part.strip() for part in address_parts if part.strip()
                )
                result["tender"]["deliveryAddresses"].append(
                    {"streetAddress": street_address}
                )

        if found_addresses:
            return result

    except Exception:
        logger.exception("Error parsing procedure place performance street")
        return None
    else:
        return None


def merge_procedure_place_performance_street(
    release_json: dict[str, Any], street_data: dict[str, Any] | None
) -> None:
    """Merge procedure place performance street data into the release JSON."""
    if not street_data:
        logger.debug("No procedure place performance street data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_addresses = tender.setdefault("deliveryAddresses", [])

    # Add new addresses if not already present
    for new_address in street_data["tender"]["deliveryAddresses"]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)

    logger.info(
        "Merged procedure place performance street data for %d addresses",
        len(street_data["tender"]["deliveryAddresses"]),
    )
