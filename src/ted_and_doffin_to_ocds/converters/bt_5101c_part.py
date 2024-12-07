from typing import Any

from lxml import etree


def parse_part_place_performance_streetline2(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse the street address information from XML for place of performance.

    Extracts address components from RealizedLocation/Address elements and combines them
    in the order: StreetName, AdditionalStreetName, AddressLine.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing tender delivery addresses or None if no addresses found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"deliveryAddresses": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
        namespaces=namespaces,
    )

    for part in parts:
        realized_locations = part.xpath(
            "cac:ProcurementProject/cac:RealizedLocation",
            namespaces=namespaces,
        )

        for location in realized_locations:
            address = location.xpath("cac:Address", namespaces=namespaces)[0]

            street_address_parts = []

            # Collect address components in specified order
            street_name = address.xpath("cbc:StreetName/text()", namespaces=namespaces)
            if street_name:
                street_address_parts.append(street_name[0])

            additional_street = address.xpath(
                "cbc:AdditionalStreetName/text()",
                namespaces=namespaces,
            )
            if additional_street:
                street_address_parts.append(additional_street[0])

            address_lines = address.xpath(
                "cac:AddressLine/cbc:Line/text()",
                namespaces=namespaces,
            )
            if address_lines:
                street_address_parts.extend(address_lines)

            if street_address_parts:
                street_address = ", ".join(
                    part.strip() for part in street_address_parts if part.strip()
                )
                if street_address:
                    result["tender"]["deliveryAddresses"].append(
                        {"streetAddress": street_address}
                    )

    return result if result["tender"]["deliveryAddresses"] else None


def merge_part_place_performance_streetline2(
    release_json: dict[str, Any],
    part_place_performance_streetline2_data: dict[str, Any] | None,
) -> None:
    """
    Merge street address data into the release JSON.

    Updates the tender.deliveryAddresses array in release_json with new addresses,
    avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        part_place_performance_streetline2_data: Source data containing delivery addresses to merge

    Returns:
        None
    """
    if not part_place_performance_streetline2_data:
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in part_place_performance_streetline2_data["tender"][
        "deliveryAddresses"
    ]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)
