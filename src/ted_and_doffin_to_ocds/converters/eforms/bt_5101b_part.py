# converters/bt_5101b_part.py

from typing import Any

from lxml import etree


def parse_part_place_performance_streetline1(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the street address information from XML for place of performance.

    Extracts street address components from RealizedLocation/Address elements and combines them
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"deliveryAddresses": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
        namespaces=namespaces,
    )

    for part in parts:
        realized_locations = part.xpath(
            "cac:ProcurementProject/cac:RealizedLocation",
            namespaces=namespaces,
        )

        for location in realized_locations:
            address = location.xpath("cac:Address", namespaces=namespaces)[0]
            street_name = address.xpath("cbc:StreetName/text()", namespaces=namespaces)
            additional_street_name = address.xpath(
                "cbc:AdditionalStreetName/text()",
                namespaces=namespaces,
            )
            address_lines = address.xpath(
                "cac:AddressLine/cbc:Line/text()",
                namespaces=namespaces,
            )

            street_address_parts = []
            street_name = address.xpath("cbc:StreetName/text()", namespaces=namespaces)
            additional_street_name = address.xpath(
                "cbc:AdditionalStreetName/text()",
                namespaces=namespaces,
            )
            address_lines = address.xpath(
                "cac:AddressLine/cbc:Line/text()",
                namespaces=namespaces,
            )

            # Ensure correct order and handle empty components
            if street_name:
                street_address_parts.append(street_name[0])
            if additional_street_name:
                street_address_parts.append(additional_street_name[0])
            if address_lines:
                street_address_parts.extend(address_lines)

            # Join with comma and space as specified
            street_address = ", ".join(filter(None, street_address_parts))

            if street_address:  # Only add if there's actual content
                result["tender"]["deliveryAddresses"].append(
                    {"streetAddress": street_address}
                )

    return result if result["tender"]["deliveryAddresses"] else None


def merge_part_place_performance_streetline1(
    release_json: dict[str, Any],
    part_place_performance_streetline1_data: dict[str, Any] | None,
) -> None:
    """Merge street address data into the release JSON.

    Updates the tender.deliveryAddresses array in release_json with new addresses,
    avoiding duplicates.

    Args:
        release_json: The target release JSON to update
        part_place_performance_streetline1_data: The source data containing delivery addresses to merge

    Returns:
        None

    """
    if not part_place_performance_streetline1_data:
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in part_place_performance_streetline1_data["tender"][
        "deliveryAddresses"
    ]:
        if new_address not in existing_addresses:
            existing_addresses.append(new_address)
