# converters/OPT_155_LotResult.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

VEHICLE_CODES = {
    "vehicles": "Vehicles",
    "vehicles-clean": "Vehicles clean",
    "vehicles-zero-emission": "Vehicles zero emission",
}


def parse_vehicle_type(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse vehicle type information from LotResult elements in XML content.

    Only includes vehicle types where StatisticsNumeric is not 0.
    Creates items with additionalClassifications for vehicle types.

    Args:
        xml_content: XML content containing LotResult data

    Returns:
        Optional[Dict]: Dictionary containing awards with vehicle type items, or None if no data
        Example:
        {
            "awards": [
                {
                    "id": "award_id",
                    "items": [
                        {
                            "id": "1",
                            "additionalClassifications": [
                                {
                                    "scheme": "vehicles",
                                    "id": "vehicle_code",
                                    "description": "Vehicle description"
                                }
                            ]
                        }
                    ],
                    "relatedLots": ["lot_id"]
                }
            ]
        }

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

        vehicle_types = lot_result.xpath(
            ".//efac:StrategicProcurementStatistics[efbc:StatisticsNumeric != '0']/efbc:StatisticsCode[@listName='vehicles']/text()",
            namespaces=namespaces,
        )

        if vehicle_types:
            award_data = {"id": award_id, "items": [], "relatedLots": [lot_id]}

            for i, vehicle_type in enumerate(vehicle_types, start=1):
                item = {
                    "id": str(i),
                    "additionalClassifications": [
                        {
                            "scheme": "vehicles",
                            "id": vehicle_type,
                            "description": VEHICLE_CODES.get(vehicle_type, ""),
                        },
                    ],
                }
                award_data["items"].append(item)

            result["awards"].append(award_data)

    return result if result["awards"] else None


def merge_vehicle_type(
    release_json: dict[str, Any], vehicle_type_data: dict[str, Any] | None
) -> None:
    """Merge vehicle type data into the release JSON.

    Args:
        release_json: Target release JSON to update
        vehicle_type_data: Vehicle type data containing awards with items

    Effects:
        Updates the awards section of release_json with vehicle type information,
        merging items and related lots where awards already exist

    """
    if not vehicle_type_data:
        logger.warning("No vehicle type data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in vehicle_type_data["awards"]:
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
                    existing_item.setdefault("additionalClassifications", []).extend(
                        new_item["additionalClassifications"],
                    )
                else:
                    existing_items.append(new_item)
            existing_award["relatedLots"] = list(
                set(existing_award.get("relatedLots", []) + new_award["relatedLots"]),
            )
        else:
            existing_awards.append(new_award)

    logger.info(
        "Merged vehicle type data for %d awards", len(vehicle_type_data["awards"])
    )
