# converters/BT_5101_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_street_lot(xml_content):
    """
    Parse the XML content to extract the place performance street for each lot,
    including BT-5101(a), BT-5101(b), and BT-5101(c).

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed place performance street data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        realized_locations = lot.xpath(".//cac:RealizedLocation", namespaces=namespaces)

        delivery_addresses = []
        for location in realized_locations:
            address_parts = []
            street_name = location.xpath(
                "cac:Address/cbc:StreetName/text()", namespaces=namespaces
            )
            if street_name:
                address_parts.append(street_name[0])

            additional_street_name = location.xpath(
                "cac:Address/cbc:AdditionalStreetName/text()", namespaces=namespaces
            )
            if additional_street_name:
                address_parts.append(additional_street_name[0])

            address_lines = location.xpath(
                "cac:Address/cac:AddressLine/cbc:Line/text()", namespaces=namespaces
            )
            address_parts.extend(address_lines)

            if address_parts:
                street_address = ", ".join(address_parts)
                delivery_addresses.append({"streetAddress": street_address})

        if delivery_addresses:
            item_data = {
                "id": str(len(result["tender"]["items"]) + 1),
                "deliveryAddresses": delivery_addresses,
                "relatedLot": lot_id,
            }
            result["tender"]["items"].append(item_data)

    return result if result["tender"]["items"] else None


def merge_place_performance_street_lot(release_json, street_data):
    """
    Merge the parsed place performance street data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        street_data (dict): The parsed place performance street data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not street_data:
        logger.warning("No place performance street data to merge for Lot")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in street_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in existing_items
                if item.get("relatedLot") == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            for new_address in new_item["deliveryAddresses"]:
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
        f"Merged place performance street data for {len(street_data['tender']['items'])} items"
    )
