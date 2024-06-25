# converters/BT_723_LotResult_Vehicle_Category.py
from lxml import etree

VEHICLE_CATEGORY_MAPPING = {
    "m1": "M1",
    "m1-m2-n1": "Light-duty Vehicle (M1, M2, N1)",
    "m2": "M2",
    "m3": "Bus (M3)",
    "n1": "N1",
    "n2": "N2",
    "n2-n3": "Truck (N2-N3)",
    "n3": "N3"
}

def parse_vehicle_category(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {}

    lot_results = root.xpath("//efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        result_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        vehicle_category = lot_result.xpath(".//efac:StrategicProcurement/efac:StrategicProcurementInformation/efac:ProcurementDetails/efbc:AssetCategoryCode[@listName='vehicle-category']/text()", namespaces=namespaces)
        
        if result_id and lot_id and vehicle_category:
            result[result_id[0]] = {
                "relatedLots": [lot_id[0]],
                "vehicleCategory": vehicle_category[0]
            }

    return result

def merge_vehicle_category(release_json, vehicle_category_data):
    if vehicle_category_data:
        awards = release_json.setdefault("awards", [])

        for result_id, data in vehicle_category_data.items():
            award = next((a for a in awards if a.get("id") == result_id), None)
            if not award:
                award = {"id": result_id}
                awards.append(award)

            award["relatedLots"] = data["relatedLots"]
            items = award.setdefault("items", [])
            
            if not items:
                items.append({"id": "1"})
            
            item = items[0]
            additional_classifications = item.setdefault("additionalClassifications", [])
            
            vehicle_category = data["vehicleCategory"]
            classification = {
                "scheme": "eu-vehicle-category",
                "id": vehicle_category,
                "description": VEHICLE_CATEGORY_MAPPING.get(vehicle_category, "")
            }
            
            existing_classification = next((c for c in additional_classifications if c["scheme"] == "eu-vehicle-category"), None)
            if existing_classification:
                existing_classification.update(classification)
            else:
                additional_classifications.append(classification)

    return release_json