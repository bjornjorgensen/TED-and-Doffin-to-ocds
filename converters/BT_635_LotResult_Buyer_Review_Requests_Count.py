# converters/BT_635_LotResult_Buyer_Review_Requests_Count.py
from lxml import etree

def parse_buyer_review_requests_count(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        statistics = lot_result.xpath("efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efbc:StatisticsNumeric/text()", namespaces=namespaces)
        
        if lot_id and statistics:
            result.append({
                "lotId": lot_id[0],
                "value": int(statistics[0])
            })

    return result

def merge_buyer_review_requests_count(release_json, review_requests_data):
    if review_requests_data:
        statistics = release_json.setdefault("statistics", [])
        
        # Find the highest existing id
        max_id = max([int(stat.get("id", 0)) for stat in statistics], default=0)

        for data in review_requests_data:
            # Check if a statistic for this lot already exists
            existing_stat = next((stat for stat in statistics if stat.get("relatedLot") == data["lotId"] and stat.get("scope") == "complaints"), None)
            
            if existing_stat:
                existing_stat["value"] = data["value"]
            else:
                max_id += 1
                new_stat = {
                    "id": str(max_id),
                    "value": data["value"],
                    "scope": "complaints",
                    "relatedLot": data["lotId"]
                }
                statistics.append(new_stat)

    return release_json