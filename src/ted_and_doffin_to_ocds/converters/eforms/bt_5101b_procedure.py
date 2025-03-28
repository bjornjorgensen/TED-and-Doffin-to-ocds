# converters/bt_5101b_procedure.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_place_performance_streetline1(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse BT-5101(b) street address information for place of performance.

    Combines StreetName, AdditionalStreetName and AddressLine values in order,
    separated by comma and space.

    Args:
        xml_content: XML content containing procurement data

    Returns:
        Dictionary with tender delivery addresses or None if no valid addresses
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"deliveryAddresses": []}}

    realized_locations = root.xpath(
        "//cac:ProcurementProject/cac:RealizedLocation", namespaces=namespaces
    )

    for location in realized_locations:
        address_elements = location.xpath("cac:Address", namespaces=namespaces)
        if not address_elements:
            logger.warning(
                "No Address element found in RealizedLocation for BT-5101(b)"
            )
            continue

        address = address_elements[0]

        # Get all address components in required order
        components = []

        street_name = address.xpath("cbc:StreetName/text()", namespaces=namespaces)
        if street_name:
            components.append(street_name[0].strip())

        additional_street = address.xpath(
            "cbc:AdditionalStreetName/text()", namespaces=namespaces
        )
        if additional_street:
            components.append(additional_street[0].strip())

        address_lines = address.xpath(
            "cac:AddressLine/cbc:Line/text()", namespaces=namespaces
        )
        components.extend(line.strip() for line in address_lines if line.strip())

        if components:  # Only create address if we have components
            street_address = ", ".join(components)
            result["tender"]["deliveryAddresses"].append(
                {"streetAddress": street_address}
            )

    return result if result["tender"]["deliveryAddresses"] else None


def merge_procedure_place_performance_streetline1(
    release_json: dict[str, Any],
    procedure_place_performance_streetline1_data: dict[str, Any] | None,
) -> None:
    """Merge street address data into the release JSON.

    Updates the tender.deliveryAddresses array in release_json with new addresses,
    avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        procedure_place_performance_streetline1_data: The source data containing delivery addresses to merge

    Returns:
        None

    """
    if not procedure_place_performance_streetline1_data:
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in procedure_place_performance_streetline1_data["tender"][
        "deliveryAddresses"
    ]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)
