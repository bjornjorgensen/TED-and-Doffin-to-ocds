# converters/bt_728_part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_part_place_performance_additional(xml_content):
    """
    Parse the XML content to extract additional place of performance information for the procurement part.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed additional place of performance data for the procurement part.
        None: If no relevant data is found.
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

    result = {"tender": {"deliveryAddresses": []}}

    descriptions = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']/cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()",
        namespaces=namespaces,
    )

    for description in descriptions:
        result["tender"]["deliveryAddresses"].append(
            {"description": description.strip()},
        )

    return result if result["tender"]["deliveryAddresses"] else None


def merge_part_place_performance_additional(
    release_json,
    part_place_performance_additional_data,
):
    """
    Merge the parsed additional place of performance data for the procurement part into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        part_place_performance_additional_data (dict): The parsed additional place of performance data for the procurement part to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not part_place_performance_additional_data:
        logger.warning(
            "No additional procurement part place of performance data to merge",
        )
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "deliveryAddresses" not in release_json["tender"]:
        release_json["tender"]["deliveryAddresses"] = []

    for new_address in part_place_performance_additional_data["tender"][
        "deliveryAddresses"
    ]:
        existing_address = next(
            (
                addr
                for addr in release_json["tender"]["deliveryAddresses"]
                if addr.get("description") == new_address["description"]
            ),
            None,
        )
        if existing_address:
            # If the address already exists, we don't need to do anything
            pass
        else:
            release_json["tender"]["deliveryAddresses"].append(new_address)

    logger.info(
        "Merged additional place of performance data for %d addresses",
        len(part_place_performance_additional_data["tender"]["deliveryAddresses"]),
    )
