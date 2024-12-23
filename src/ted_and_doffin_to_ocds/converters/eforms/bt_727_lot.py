# converters/bt_727_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

REGION_MAPPING = {
    "anyw": "Anywhere",
    "anyw-cou": "Anywhere in the given country",
    "anyw-eea": "Anywhere in the European Economic Area",
}


def parse_lot_place_performance(xml_content: str | bytes) -> dict | None:
    """Parse place of performance information for lots.

    Extracts region codes from RealizedLocation elements and maps them to
    delivery locations. Handles special region codes like "anywhere in EEA".

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "items": [
                        {
                            "id": str,
                            "relatedLot": str,
                            "deliveryLocations": [
                                {
                                    "description": str
                                }
                            ]
                        }
                    ]
                }
            }
        Returns None if no relevant data found

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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        regions = lot.xpath(
            "cac:ProcurementProject/cac:RealizedLocation/cac:Address/cbc:Region/text()",
            namespaces=namespaces,
        )

        if regions:
            item = {
                "id": str(len(result["tender"]["items"]) + 1),
                "relatedLot": lot_id,
                "deliveryLocations": [],
            }

            for region in regions:
                description = REGION_MAPPING.get(region, region)
                item["deliveryLocations"].append({"description": description})

            result["tender"]["items"].append(item)

    return result if result["tender"]["items"] else None


def merge_lot_place_performance(
    release_json: dict, lot_place_performance_data: dict | None
) -> None:
    """Merge place of performance data into the main OCDS release JSON.

    Updates or adds delivery locations for items based on their related lots.
    Handles concatenation of multiple region descriptions if needed.

    Args:
        release_json: Main OCDS release JSON to update
        lot_place_performance_data: Place performance data to merge, can be None
    """
    if not lot_place_performance_data:
        logger.warning("No lot place of performance data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "items" not in release_json["tender"]:
        release_json["tender"]["items"] = []

    for new_item in lot_place_performance_data["tender"]["items"]:
        if "relatedLot" not in new_item:
            logger.warning("Skipping item without relatedLot: %s", new_item)
            continue

        try:
            existing_item = next(
                (
                    item
                    for item in release_json["tender"]["items"]
                    if "relatedLot" in item
                    and item["relatedLot"] == new_item["relatedLot"]
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
                    if not existing_location:
                        existing_item["deliveryLocations"].append(new_location)
            else:
                release_json["tender"]["items"].append(new_item)

        except KeyError:
            logger.exception("KeyError encountered while merging lot data")

    logger.info(
        "Merged place performance data for %d lots",
        len(lot_place_performance_data["tender"]["items"]),
    )
