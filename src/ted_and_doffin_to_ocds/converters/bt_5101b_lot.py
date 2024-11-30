# converters/bt_5101b_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_place_performance_streetline1(xml_content):
    """
    Parse the street address components for lot delivery addresses.
    Combines StreetName, AdditionalStreetName and AddressLine components in order.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"items": []}}

        # Find all procurement project lots
        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=namespaces,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]

            # Find all realized locations for this lot
            locations = lot.xpath(
                "cac:ProcurementProject/cac:RealizedLocation/cac:Address",
                namespaces=namespaces,
            )

            if locations:
                item = {
                    "id": str(len(result["tender"]["items"]) + 1),
                    "relatedLot": lot_id,
                    "deliveryAddresses": [],
                }

                for address in locations:
                    # Get all address components in specified order
                    street_parts = []

                    # 1. StreetName
                    street_name = address.xpath(
                        "cbc:StreetName/text()", namespaces=namespaces
                    )
                    if street_name:
                        street_parts.append(street_name[0])

                    # 2. AdditionalStreetName
                    additional = address.xpath(
                        "cbc:AdditionalStreetName/text()", namespaces=namespaces
                    )
                    if additional:
                        street_parts.append(additional[0])

                    # 3. All AddressLine/Line elements
                    lines = address.xpath(
                        "cac:AddressLine/cbc:Line/text()", namespaces=namespaces
                    )
                    street_parts.extend(lines)

                    # Combine all parts with comma and space
                    if street_parts:
                        street_address = ", ".join(
                            part.strip()
                            for part in street_parts
                            if part and part.strip()
                        )
                        item["deliveryAddresses"].append(
                            {"streetAddress": street_address}
                        )

                if item["deliveryAddresses"]:
                    result["tender"]["items"].append(item)
                    logger.info("Added delivery addresses for lot %s", lot_id)

        return result if result["tender"]["items"] else None

    except Exception:
        logger.exception("Error parsing lot place performance street address")
        return None


def merge_lot_place_performance_streetline1(
    release_json,
    lot_place_performance_streetline1_data,
) -> None:
    if not lot_place_performance_streetline1_data:
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in lot_place_performance_streetline1_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            existing_item["deliveryAddresses"] = new_item["deliveryAddresses"]
        else:
            existing_items.append(new_item)
