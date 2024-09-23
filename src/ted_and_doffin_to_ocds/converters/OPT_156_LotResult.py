# converters/OPT_156_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_vehicle_numeric(xml_content):
    """
    Parse the XML content to extract the vehicle numeric information for each lot result.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed vehicle numeric data.
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

    result = {"awards": []}

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )
    for lot_result in lot_results:
        award_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )[0]
        lot_id = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )[0]

        statistics = lot_result.xpath(
            ".//efac:StrategicProcurementStatistics",
            namespaces=namespaces,
        )

        award_data = {"id": award_id, "items": [], "relatedLots": [lot_id]}

        total_vehicles = 0
        special_vehicles = 0
        item_id = 1

        for stat in statistics:
            code = stat.xpath("efbc:StatisticsCode/text()", namespaces=namespaces)[0]
            numeric = int(
                stat.xpath("efbc:StatisticsNumeric/text()", namespaces=namespaces)[0],
            )

            if numeric > 0:
                if code == "vehicles":
                    total_vehicles = numeric
                elif code in ["vehicles-zero-emission", "vehicles-clean"]:
                    special_vehicles += numeric
                    item = {
                        "id": str(item_id),
                        "quantity": numeric,
                        "classification": {
                            "scheme": "vehicles",
                            "id": code,
                            "description": code.replace("-", " ").title(),
                        },
                    }
                    award_data["items"].append(item)
                    item_id += 1

        if total_vehicles > special_vehicles:
            regular_vehicles = total_vehicles - special_vehicles
            item = {
                "id": str(item_id),
                "quantity": regular_vehicles,
                "classification": {
                    "scheme": "vehicles",
                    "id": "vehicles",
                    "description": "Vehicles",
                },
            }
            award_data["items"].append(item)

        if award_data["items"]:
            result["awards"].append(award_data)

    return result if result["awards"] else None


def merge_vehicle_numeric(release_json, vehicle_numeric_data):
    """
    Merge the parsed vehicle numeric data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        vehicle_numeric_data (dict): The parsed vehicle numeric data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not vehicle_numeric_data:
        logger.warning("No vehicle numeric data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in vehicle_numeric_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_items = existing_award.setdefault("items", [])
            for new_item in new_award["items"]:
                existing_item = next(
                    (item for item in existing_items if item["id"] == new_item["id"]),
                    None,
                )
                if existing_item:
                    existing_item.update(new_item)
                else:
                    existing_items.append(new_item)
            existing_award["relatedLots"] = list(
                set(existing_award.get("relatedLots", []) + new_award["relatedLots"]),
            )
        else:
            existing_awards.append(new_award)

    logger.info(
        f"Merged vehicle numeric data for {len(vehicle_numeric_data['awards'])} awards",
    )
