# converters/OPT_155_156_LotResult.py

from lxml import etree

def parse_vehicle_type_and_numeric(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"awards": []}

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        award_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        
        if not award_id or not lot_id:
            continue

        award_id = award_id[0]
        lot_id = lot_id[0]

        items = []
        item_id = 1

        stats = lot_result.xpath(".//efac:StrategicProcurementStatistics", namespaces=namespaces)
        for stat in stats:
            numeric_value = stat.xpath("efbc:StatisticsNumeric/text()", namespaces=namespaces)
            if not numeric_value or float(numeric_value[0]) == 0:
                continue

            vehicle_types = stat.xpath("efbc:StatisticsCode[@listName='vehicles']/text()", namespaces=namespaces)
            if not vehicle_types:
                continue

            item = {
                "id": str(item_id),
                "additionalClassifications": []
            }

            for vehicle_type in vehicle_types:
                item["additionalClassifications"].append({
                    "scheme": "vehicles",
                    "id": vehicle_type,
                    "description": vehicle_type.replace('-', ' ')  # Simple transformation, replace with actual lookup if available
                })

            items.append(item)
            item_id += 1

        if items:
            result["awards"].append({
                "id": award_id,
                "items": items,
                "relatedLots": [lot_id]
            })

    return result if result["awards"] else None

def merge_vehicle_type_and_numeric(release_json, vehicle_data):
    if not vehicle_data:
        return

    awards = release_json.setdefault("awards", [])

    for new_award in vehicle_data["awards"]:
        existing_award = next((award for award in awards if award["id"] == new_award["id"]), None)
        if existing_award:
            existing_items = existing_award.setdefault("items", [])
            for new_item in new_award["items"]:
                existing_item = next((item for item in existing_items if item["id"] == new_item["id"]), None)
                if existing_item:
                    existing_item["additionalClassifications"] = new_item["additionalClassifications"]
                else:
                    existing_items.append(new_item)
            existing_award.setdefault("relatedLots", []).extend(
                lot for lot in new_award["relatedLots"] if lot not in existing_award.get("relatedLots", [])
            )
        else:
            awards.append(new_award)