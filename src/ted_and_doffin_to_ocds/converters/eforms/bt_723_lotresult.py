# converters/bt_723_LotResult.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

VEHICLE_CATEGORY_MAPPING = {
    "m1": "M1",
    "m1-m2-n1": "Light-duty Vehicle (M1, M2, N1)",
    "m2": "M2",
    "m3": "Bus (M3)",
    "n1": "N1",
    "n2": "N2",
    "n2-n3": "Truck (N2-N3)",
    "n3": "N3",
}


def parse_vehicle_category(xml_content: str | bytes) -> dict | None:
    """Parse the XML content to extract vehicle category information for lot results.

    This function processes XML content to extract vehicle category information from lot results,
    specifically targeting the AssetCategoryCode elements with listName="vehicle-category".
    It creates a structured dictionary containing award information with vehicle classifications.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as a string or bytes

    Returns:
        Optional[Dict]: A dictionary containing the parsed vehicle category data in the format:
            {
                "awards": [
                    {
                        "id": str,
                        "relatedLots": [str],
                        "items": [
                            {
                                "id": str,
                                "additionalClassifications": [
                                    {
                                        "scheme": str,
                                        "id": str,
                                        "description": str
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            Returns None if no relevant data is found.

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

    result = {"awards": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        result_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )
        vehicle_category = lot_result.xpath(
            "efac:StrategicProcurement/efac:StrategicProcurementInformation/efac:ProcurementDetails/efbc:AssetCategoryCode[@listName='vehicle-category']/text()",
            namespaces=namespaces,
        )

        if result_id and lot_id and vehicle_category:
            award = {
                "id": result_id[0],
                "relatedLots": [lot_id[0]],
                "items": [
                    {
                        "id": "1",
                        "additionalClassifications": [
                            {
                                "scheme": "eu-vehicle-category",
                                "id": vehicle_category[0],
                                "description": VEHICLE_CATEGORY_MAPPING.get(
                                    vehicle_category[0].lower(),
                                    "Unknown",
                                ),
                            },
                        ],
                    },
                ],
            }
            result["awards"].append(award)

    return result if result["awards"] else None


def merge_vehicle_category(
    release_json: dict, vehicle_category_data: dict | None
) -> None:
    """Merge the parsed vehicle category data into the main OCDS release JSON.

    This function takes vehicle category data and merges it into the main OCDS release JSON.
    For each award in the vehicle category data, it either updates an existing award or
    adds a new one. When updating existing awards, it handles the items and their
    additionalClassifications appropriately.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated
        vehicle_category_data (Optional[Dict]): The parsed vehicle category data to be merged.
                                              If None, the function returns without changes.

    Returns:
        None: The function updates the release_json in-place.

    Note:
        - If vehicle_category_data is None, a warning is logged and no changes are made
        - For existing awards, additionalClassifications are extended
        - Related lots are deduplicated using a set operation

    """
    if not vehicle_category_data:
        logger.warning("No vehicle category data to merge")
        return

    if "awards" not in release_json:
        release_json["awards"] = []

    for new_award in vehicle_category_data["awards"]:
        existing_award = next(
            (
                award
                for award in release_json["awards"]
                if award["id"] == new_award["id"]
            ),
            None,
        )
        if existing_award:
            if "items" not in existing_award:
                existing_award["items"] = []
            if existing_award["items"]:
                existing_item = existing_award["items"][0]
                if "additionalClassifications" not in existing_item:
                    existing_item["additionalClassifications"] = []
                existing_item["additionalClassifications"].extend(
                    new_award["items"][0]["additionalClassifications"],
                )
            else:
                existing_award["items"].extend(new_award["items"])
            existing_award["relatedLots"] = list(
                set(existing_award.get("relatedLots", []) + new_award["relatedLots"]),
            )
        else:
            release_json["awards"].append(new_award)

    logger.info(
        "Merged vehicle category data for %d awards",
        len(vehicle_category_data["awards"]),
    )
