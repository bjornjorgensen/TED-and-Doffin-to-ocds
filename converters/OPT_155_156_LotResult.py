# converters/OPT_155_156_LotResult.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_vehicle_type_and_numeric(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {"awards": []}

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        award_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if not award_id or not lot_id:
            logger.warning(f"Missing award_id or lot_id for a LotResult")
            continue
        
        award_id = award_id[0]
        lot_id = lot_id[0]
        
        statistics = lot_result.xpath(".//efac:StrategicProcurementStatistics", namespaces=namespaces)
        
        items = {}
        total_vehicles = 0
        zero_emission_clean_vehicles = 0

        for stat in statistics:
            numeric_value = stat.xpath("efbc:StatisticsNumeric/text()", namespaces=namespaces)
            if not numeric_value or int(numeric_value[0]) == 0:
                continue

            numeric_value = int(numeric_value[0])
            code = stat.xpath("efbc:StatisticsCode[@listName='vehicles']/text()", namespaces=namespaces)

            if code:
                code = code[0]
                if code == "vehicles":
                    total_vehicles = numeric_value
                elif code in ["vehicles-zero-emission", "vehicles-clean"]:
                    zero_emission_clean_vehicles += numeric_value
                    items[code] = {
                        "id": code,
                        "quantity": numeric_value,
                        "additionalClassifications": [{
                            "scheme": "vehicles",
                            "id": code,
                            "description": code.replace('-', ' ')
                        }]
                    }

        # Calculate the number of other vehicles
        other_vehicles = total_vehicles - zero_emission_clean_vehicles
        if other_vehicles > 0:
            items["vehicles-other"] = {
                "id": "vehicles-other",
                "quantity": other_vehicles,
                "additionalClassifications": [{
                    "scheme": "vehicles",
                    "id": "vehicles-other",
                    "description": "vehicles other"
                }]
            }

        if items:
            result["awards"].append({
                "id": award_id,
                "items": list(items.values()),
                "relatedLots": [lot_id]
            })

    return result if result["awards"] else None

def merge_vehicle_type_and_numeric(release_json, vehicle_data):
    if not vehicle_data:
        logger.warning("No Vehicle Type and Numeric data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])
    
    for new_award in vehicle_data["awards"]:
        existing_award = next((award for award in existing_awards if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_items = existing_award.setdefault("items", [])
            for new_item in new_award["items"]:
                existing_item = next((item for item in existing_items if item["id"] == new_item["id"]), None)
                if existing_item:
                    existing_item.update(new_item)
                else:
                    existing_items.append(new_item)
            existing_award.setdefault("relatedLots", []).extend(
                lot for lot in new_award["relatedLots"] if lot not in existing_award.get("relatedLots", [])
            )
        else:
            existing_awards.append(new_award)

    logger.info(f"Merged Vehicle Type and Numeric data for {len(vehicle_data['awards'])} awards")