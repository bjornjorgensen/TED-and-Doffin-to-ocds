# converters/bt_728_Lot.py

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


def parse_lot_place_performance_additional(
    xml_content: str | bytes,
) -> dict | None:
    """Parse additional place of performance information for lots (BT-728).

    This field maps to the same Address objects as created for BT-727-Lot,
    BT-5121-Lot, BT-5071-Lot, BT-5131-Lot, BT-5101-Lot and BT-5141-Lot.

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
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)
        result = {"tender": {"items": []}}

        lots = root.xpath(
            "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]
            descriptions = lot.xpath(
                "cac:ProcurementProject/cac:RealizedLocation/cbc:Description/text()",
                namespaces=NAMESPACES,
            )

            if descriptions:
                item = {
                    "id": str(len(result["tender"]["items"]) + 1),
                    "relatedLot": lot_id,
                    "deliveryLocations": [],
                }

                for description in descriptions:
                    item["deliveryLocations"].append(
                        {"description": description.strip()}
                    )

                result["tender"]["items"].append(item)

        return result if result["tender"]["items"] else None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing additional place of performance")
        return None


def merge_lot_place_performance_additional(
    release_json: dict, additional_data: dict | None
) -> None:
    """Merge additional place of performance data into the main OCDS release JSON.

    Updates or adds delivery locations for items based on their related lots.
    Handles concatenating descriptions if needed.

    Args:
        release_json: Main OCDS release JSON to update
        additional_data: Additional place performance data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.items array if needed
        - Handles duplicates by checking existing descriptions

    """
    if not additional_data:
        logger.warning("No additional lot place of performance data to merge")
        return

    if "tender" not in release_json:
        release_json["tender"] = {}
    if "items" not in release_json["tender"]:
        release_json["tender"]["items"] = []

    for new_item in additional_data["tender"]["items"]:
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
        "Merged additional place of performance data for %d lots",
        len(additional_data["tender"]["items"]),
    )
