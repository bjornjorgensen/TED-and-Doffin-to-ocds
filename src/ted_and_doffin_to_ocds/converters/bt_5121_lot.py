# converters/bt_5121_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_post_code(xml_content):
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

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        postal_zones = lot.xpath(
            "cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:PostalZone/text()",
            namespaces=namespaces,
        )

        if postal_zones:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "deliveryAddresses": [
                    {"postalCode": postal_zone} for postal_zone in postal_zones
                ],
                "relatedLot": lot_id,
            }
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_place_performance_post_code(release_json, post_code_data):
    if not post_code_data:
        logger.warning("No Place Performance Post Code data to merge")
        return

    existing_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in post_code_data["tender"]["items"]:
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
        else:
            existing_items.append(new_item)

    logger.info(
        f"Merged Place Performance Post Code data for {len(post_code_data['tender']['items'])} items",
    )
