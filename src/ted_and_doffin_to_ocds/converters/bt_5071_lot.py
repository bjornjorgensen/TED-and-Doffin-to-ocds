# converters/bt_5071_lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_country_subdivision(xml_content):
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
        country_subdivisions = lot.xpath(
            ".//cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode",
            namespaces=namespaces,
        )

        if country_subdivisions:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "relatedLot": lot_id,
                "deliveryAddresses": [],
            }
            for subdivision in country_subdivisions:
                item["deliveryAddresses"].append({"region": subdivision.text})
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_place_performance_country_subdivision(release_json, subdivision_data) -> None:
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
