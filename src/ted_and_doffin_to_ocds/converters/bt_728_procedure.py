# converters/bt_728_procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_procedure_place_performance_additional(xml_content):
    """
    Parse the XML content to extract additional place of performance information.

    Maps to .description in tender.deliveryAddresses objects.

    Args:
        xml_content (str|bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed place performance data
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    root = etree.fromstring(xml_content)

    # Get RealizedLocation descriptions using exact specified XPath
    descriptions = root.xpath(
        "/*/cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()",
        namespaces=NAMESPACES,
    )

    if not descriptions:
        return None

    result = {"tender": {"deliveryAddresses": []}}

    # Create delivery address object for each non-empty description
    for desc in descriptions:
        if desc and desc.strip():
            result["tender"]["deliveryAddresses"].append({"description": desc.strip()})

    return result if result["tender"]["deliveryAddresses"] else None


def merge_procedure_place_performance_additional(release_json, place_performance_data):
    """
    Merge the additional place performance data into the OCDS release,
    concatenating descriptions for matching addresses.

    Args:
        release_json (dict): The main OCDS release JSON to be updated
        place_performance_data (dict): The parsed place performance data to be merged
    """
    if not place_performance_data:
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "deliveryAddresses" not in release_json["tender"]:
        release_json["tender"]["deliveryAddresses"] = []

    for new_addr in place_performance_data["tender"]["deliveryAddresses"]:
        # Try to find matching existing address to concatenate description
        existing = next(
            (
                addr
                for addr in release_json["tender"]["deliveryAddresses"]
                if addr.get("description") == new_addr["description"]
            ),
            None,
        )

        if existing:
            # If addresses match, ensure descriptions are properly concatenated
            if new_addr["description"] not in existing["description"]:
                existing["description"] = (
                    f"{existing['description']}; {new_addr['description']}"
                )
        else:
            # Add new address if no match found
            release_json["tender"]["deliveryAddresses"].append(new_addr)

    logger.info(
        "Merged additional place of performance data for %d addresses",
        len(place_performance_data["tender"]["deliveryAddresses"]),
    )
