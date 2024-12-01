# converters/bt_728_part.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_place_performance_additional(xml_content):
    """
    Parse BT-728-Part: Additional place of performance information.
    Maps realized location descriptions to tender.deliveryAddresses[].description
    """
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

    addresses = []

    locations = root.xpath(
        "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
        "/cac:ProcurementProject/cac:RealizedLocation",
        namespaces=namespaces,
    )

    for location in locations:
        description = location.xpath("string(cbc:Description)", namespaces=namespaces)
        if description.strip():
            addresses.append({"description": description.strip()})

    if addresses:
        return {"tender": {"deliveryAddresses": addresses}}

    return None


def merge_part_place_performance_additional(release_json, additional_data) -> None:
    """
    Merge BT-728-Part data into the release.
    Updates or concatenates descriptions for matching addresses.
    """
    if not additional_data:
        return

    tender = release_json.setdefault("tender", {})
    addresses = tender.setdefault("deliveryAddresses", [])

    for new_address in additional_data["tender"]["deliveryAddresses"]:
        # Check if there's an existing address to update
        existing = next((addr for addr in addresses if addr.get("description")), None)

        if existing:
            # Concatenate the description
            existing["description"] = (
                f"{existing['description']}; {new_address['description']}"
            )
        else:
            # Add as new address
            addresses.append(new_address)

    logger.info(
        "Merged additional place of performance data for %d addresses",
        len(additional_data["tender"]["deliveryAddresses"]),
    )
