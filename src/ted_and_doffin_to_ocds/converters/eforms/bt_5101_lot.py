import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_place_performance_street_lot(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse place performance street (BT-5101) from XML content."""
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"items": []}}

        # Get all lots using exact BT-5101 path
        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        found_addresses = False
        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
                realized_locations = lot.xpath(
                    "cac:ProcurementProject/cac:RealizedLocation", namespaces=NAMESPACES
                )

                delivery_addresses = []
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
                        "cac:Address/cbc:AdditionalStreetName/text()",
                        namespaces=NAMESPACES,
                    )
                    if additional_street:
                        address_parts.append(additional_street[0])

                    # Get address lines
                    address_lines = location.xpath(
                        "cac:Address/cac:AddressLine/cbc:Line/text()",
                        namespaces=NAMESPACES,
                    )
                    address_parts.extend(address_lines)

                    if address_parts:
                        found_addresses = True
                        street_address = ", ".join(
                            part.strip() for part in address_parts if part.strip()
                        )
                        delivery_addresses.append({"streetAddress": street_address})

                if delivery_addresses:
                    result["tender"]["items"].append(
                        {
                            "id": str(len(result["tender"]["items"]) + 1),
                            "deliveryAddresses": delivery_addresses,
                            "relatedLot": lot_id,
                        }
                    )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot data: %s", e)
                continue

        if found_addresses:
            return result

    except Exception:
        logger.exception("Error parsing place performance street")
        return None
    else:
        return None


def merge_place_performance_street_lot(
    release_json: dict[str, Any], street_data: dict[str, Any] | None
) -> None:
    """Merge place performance street data into the release JSON."""
    if not street_data:
        logger.debug("No place performance street data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in street_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )

        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            for new_address in new_item["deliveryAddresses"]:
                # Find address without street or add new one
                existing_address = next(
                    (
                        addr
                        for addr in existing_addresses
                        if "streetAddress" not in addr
                    ),
                    None,
                )
                if existing_address:
                    existing_address["streetAddress"] = new_address["streetAddress"]
                else:
                    existing_addresses.append(new_address)
        else:
            existing_items.append(new_item)

    logger.info(
        "Merged place performance street data for %d items",
        len(street_data["tender"]["items"]),
    )
