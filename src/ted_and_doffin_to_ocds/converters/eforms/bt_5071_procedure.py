# converters/bt_5071_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_place_performance_country_subdivision_procedure(
    xml_content: str | bytes,
) -> dict | None:
    """Parse country subdivision codes (NUTS3) from procurement project.
    Maps to region in tender.deliveryAddresses objects.

    Args:
        xml_content: The XML content to parse

    Returns:
        dict: Dictionary containing the parsed delivery addresses with region info
        None: If no valid data is found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    subdivisions = root.xpath(
        "/*/cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:CountrySubentityCode/text()",
        namespaces=namespaces,
    )

    addresses = [{"region": code.strip()} for code in subdivisions if code.strip()]

    if addresses:
        return {"tender": {"deliveryAddresses": addresses}}

    return None


def merge_place_performance_country_subdivision_procedure(
    release_json: dict, subdivision_data: dict | None
) -> None:
    """Merge country subdivision data into the OCDS release.
    Updates or adds region info to matching delivery addresses.

    Args:
        release_json: The main OCDS release JSON to update
        subdivision_data: The parsed subdivision data to merge

    """
    if not subdivision_data:
        logger.info("No place performance country subdivision data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_addresses = tender.setdefault("deliveryAddresses", [])

    for new_address in subdivision_data["tender"]["deliveryAddresses"]:
        existing_address = next(
            (addr for addr in existing_addresses if "region" not in addr),
            None,
        )
        if existing_address:
            existing_address["region"] = new_address["region"]
        else:
            existing_addresses.append(new_address)

    logger.info(
        "Merged place performance country subdivision data for %d addresses",
        len(subdivision_data["tender"]["deliveryAddresses"]),
    )
