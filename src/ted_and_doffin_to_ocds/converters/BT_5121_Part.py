# converters/BT_5121_Part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_post_code_part(xml_content):
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
        postal_zones = part.xpath(
            "cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:PostalZone/text()",
            namespaces=namespaces,
        )

        for postal_zone in postal_zones:
            address = {"postalCode": postal_zone}
            result["tender"]["deliveryAddresses"].append(address)

    return result if result["tender"]["deliveryAddresses"] else None


def merge_place_performance_post_code_part(release_json, post_code_data):
    if not post_code_data:
        logger.warning("No Place Performance Post Code (Part) data to merge")
        return

    existing_addresses = release_json.setdefault("tender", {}).setdefault(
        "deliveryAddresses",
        [],
    )

    for new_address in post_code_data["tender"]["deliveryAddresses"]:
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

    logger.info(
        f"Merged Place Performance Post Code (Part) data for {len(post_code_data['tender']['deliveryAddresses'])} addresses",
    )
