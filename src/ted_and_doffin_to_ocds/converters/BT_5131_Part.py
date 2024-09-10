# converters/BT_5131_Part.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_place_performance_city_part(xml_content):
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces
    )

    for part in parts:
        cities = part.xpath(
            ".//cac:RealizedLocation/cac:Address/cbc:CityName/text()",
            namespaces=namespaces,
        )

        for city in cities:
            result["tender"]["deliveryAddresses"].append({"locality": city})

    return result if result["tender"]["deliveryAddresses"] else None


def merge_place_performance_city_part(release_json, place_performance_city_part_data):
    if not place_performance_city_part_data:
        logger.warning("No Place Performance City Part data to merge")
        return

    tender_delivery_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses", []
    )

    for new_address in place_performance_city_part_data["tender"]["deliveryAddresses"]:
        matching_address = next(
            (
                addr
                for addr in tender_delivery_addresses
                if addr.get("locality") == new_address["locality"]
            ),
            None,
        )
        if matching_address:
            matching_address.update(new_address)
        else:
            tender_delivery_addresses.append(new_address)

    logger.info(
        f"Merged Place Performance City Part data for {len(place_performance_city_part_data['tender']['deliveryAddresses'])} addresses"
    )
