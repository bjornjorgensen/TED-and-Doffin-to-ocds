# converters/BT_728_Lot.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_place_performance_additional(xml_content):
    """
    Parse the XML content to extract additional place of performance information for lots.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed additional place of performance data for lots.
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

    result = {"tender": {"items": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        descriptions = lot.xpath(
            "cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()",
            namespaces=namespaces,
        )

        if descriptions:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "relatedLot": lot_id,
                "deliveryLocations": [],
            }

            for description in descriptions:
                item["deliveryLocations"].append({"description": description.strip()})

            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_lot_place_performance_additional(
    release_json, lot_place_performance_additional_data
):
    """
    Merge the parsed additional place of performance data for lots into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        lot_place_performance_additional_data (dict): The parsed additional place of performance data for lots to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not lot_place_performance_additional_data:
        logger.warning("No additional lot place of performance data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "items" not in release_json["tender"]:
        release_json["tender"]["items"] = []

    for new_item in lot_place_performance_additional_data["tender"]["items"]:
        existing_item = next(
            (
                item
                for item in release_json["tender"]["items"]
                if item["relatedLot"] == new_item["relatedLot"]
            ),
            None,
        )
        if existing_item:
            if "deliveryLocations" not in existing_item:
                existing_item["deliveryLocations"] = []
            for new_location in new_item["deliveryLocations"]:
                existing_location = next(
                    (
                        loc
                        for loc in existing_item["deliveryLocations"]
                        if loc.get("description") == new_location["description"]
                    ),
                    None,
                )
                if existing_location:
                    # If the location already exists, we don't need to do anything
                    pass
                else:
                    existing_item["deliveryLocations"].append(new_location)
        else:
            release_json["tender"]["items"].append(new_item)

    logger.info(
        f"Merged additional place of performance data for {len(lot_place_performance_additional_data['tender']['items'])} lots"
    )
