# converters/bt_5131_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_place_performance_city(xml_content):
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
        cities = lot.xpath(
            ".//cac:RealizedLocation/cac:Address/cbc:CityName/text()",
            namespaces=namespaces,
        )

        if cities:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "relatedLot": lot_id,
                "deliveryAddresses": [{"locality": city} for city in cities],
            }
            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_place_performance_city(release_json, place_performance_city_data):
    if not place_performance_city_data:
        logger.warning("No Place Performance City data to merge")
        return

    tender_items = release_json.setdefault("tender", {}).setdefault("items", [])

    for new_item in place_performance_city_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in tender_items
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )

        if existing_item:
            existing_addresses = existing_item.setdefault("deliveryAddresses", [])
            for new_address in new_item["deliveryAddresses"]:
                if existing_addresses:
                    existing_addresses[0].update(new_address)
                else:
                    existing_addresses.append(new_address)
        else:
            tender_items.append(new_item)

    logger.info(
        f"Merged Place Performance City data for {len(place_performance_city_data['tender']['items'])} items",
    )
