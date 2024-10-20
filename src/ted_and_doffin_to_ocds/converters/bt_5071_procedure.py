# converters/bt_5071_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_country_subdivision_procedure(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {}

    realized_locations = root.xpath(
        "/*/cac:ProcurementProject/cac:RealizedLocation", namespaces=namespaces
    )
    delivery_addresses = []
    for location in realized_locations:
        country_subdivisions = location.xpath(
            "cac:Address/cbc:CountrySubentityCode", namespaces=namespaces
        )
        delivery_addresses = [
            {"region": subdivision.text} for subdivision in country_subdivisions
        ]

    if delivery_addresses:
        result["tender"] = {"deliveryAddresses": delivery_addresses}

    return result if result else None


def merge_place_performance_country_subdivision_procedure(
    release_json, subdivision_data
):
    if (
        not subdivision_data
        or "tender" not in subdivision_data
        or "deliveryAddresses" not in subdivision_data["tender"]
    ):
        logger.info(
            "No place performance country subdivision data for Procedure to merge"
        )
        return

    tender = release_json.setdefault("tender", {})
    new_addresses = subdivision_data["tender"]["deliveryAddresses"]

    if "deliveryAddresses" not in tender:
        tender["deliveryAddresses"] = new_addresses
    else:
        existing_addresses = tender["deliveryAddresses"]
        for new_address in new_addresses:
            if new_address not in existing_addresses:
                existing_addresses.append(new_address)

    logger.info(
        "Merged place performance country subdivision data for %d Procedure locations",
        len(new_addresses),
    )
