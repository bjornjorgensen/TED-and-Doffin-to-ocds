# converters/bt_5071_part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_country_subdivision_part(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"deliveryAddresses": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces
    )
    for part in parts:
        country_subdivisions = part.xpath(
            ".//cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode",
            namespaces=namespaces,
        )
        for subdivision in country_subdivisions:
            result["tender"]["deliveryAddresses"].append({"region": subdivision.text})

    return result if result["tender"]["deliveryAddresses"] else None


def merge_place_performance_country_subdivision_part(release_json, subdivision_data):
    if not subdivision_data:
        logger.info("No place performance country subdivision data for Parts to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_addresses = tender.setdefault("deliveryAddresses", [])

    for new_address in subdivision_data["tender"]["deliveryAddresses"]:
        existing_address = next(
            (addr for addr in existing_addresses if "region" not in addr), None
        )
        if existing_address:
            existing_address["region"] = new_address["region"]
        else:
            existing_addresses.append(new_address)

    logger.info(
        "Merged place performance country subdivision data for %d Parts",
        len(subdivision_data["tender"]["deliveryAddresses"]),
    )
