# converters/bt_5071_lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_country_subdivision(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse country subdivision codes from Lot procurement projects.
    Maps to region in tender.items[].deliveryAddresses objects.

    Args:
        xml_content: The XML content to parse

    Returns:
        dict: Dictionary containing the parsed tender items with region info
        None: If no valid data is found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    lots = root.xpath(
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    items = []
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        subdivisions = lot.xpath(
            "cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode/text()",
            namespaces=namespaces,
        )

        if subdivisions:
            addresses = [{"region": code} for code in subdivisions if code.strip()]
            if addresses:
                items.append(
                    {
                        "id": str(len(items) + 1),
                        "relatedLot": lot_id,
                        "deliveryAddresses": addresses,
                    }
                )

    if items:
        return {"tender": {"items": items}}

    return None


def merge_place_performance_country_subdivision(
    release_json: dict, subdivision_data: dict | None
) -> None:
    """
    Merge country subdivision data into the OCDS release.
    Updates or adds region info to matching delivery addresses.

    Args:
        release_json: The main OCDS release JSON to update
        subdivision_data: The parsed subdivision data to merge
    """
    if not subdivision_data:
        logger.info("No place performance country subdivision data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_items = tender.setdefault("items", [])

    for new_item in subdivision_data["tender"]["items"]:
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
                existing_address = next(
                    (addr for addr in existing_addresses if "region" not in addr), None
                )
                if existing_address:
                    existing_address["region"] = new_address["region"]
                else:
                    existing_addresses.append(new_address)
        else:
            existing_items.append(new_item)

    logger.info(
        "Merged place performance country subdivision data for %d items",
        len(subdivision_data["tender"]["items"]),
    )
