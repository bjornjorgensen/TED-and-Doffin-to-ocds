# converters/bt_727_part.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

REGION_MAPPING = {
    "anyw": "Anywhere",
    "anyw-cou": "Anywhere in the given country",
    "anyw-eea": "Anywhere in the European Economic Area",
}


def parse_part_place_performance(xml_content):
    """
    Parse the XML content to extract place of performance information for the procurement part.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed place of performance data for the procurement part.
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

    result = {"tender": {"deliveryLocations": []}}

    regions = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']/cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:Region/text()",
        namespaces=namespaces,
    )

    for region in regions:
        description = REGION_MAPPING.get(region, region)
        result["tender"]["deliveryLocations"].append({"description": description})

    return result if result["tender"]["deliveryLocations"] else None


def merge_part_place_performance(release_json, part_place_performance_data):
    """
    Merge the parsed place of performance data for the procurement part into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        part_place_performance_data (dict): The parsed place of performance data for the procurement part to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not part_place_performance_data:
        logger.warning("No procurement part place of performance data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "deliveryLocations" not in release_json["tender"]:
        release_json["tender"]["deliveryLocations"] = []

    for new_location in part_place_performance_data["tender"]["deliveryLocations"]:
        existing_location = next(
            (
                loc
                for loc in release_json["tender"]["deliveryLocations"]
                if loc.get("description") == new_location["description"]
            ),
            None,
        )
        if existing_location:
            # If the location already exists, we don't need to do anything
            pass
        else:
            release_json["tender"]["deliveryLocations"].append(new_location)

    logger.info(
        f"Merged place of performance data for {len(part_place_performance_data['tender']['deliveryLocations'])} locations",
    )
