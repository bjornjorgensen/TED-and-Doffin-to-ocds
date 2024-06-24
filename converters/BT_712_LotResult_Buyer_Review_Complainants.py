# converters/BT_712_LotResult_Buyer_Review_Complainants.py
from lxml import etree

def parse_buyer_review_complainants(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = []

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        statistics = lot_result.xpath("efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']", namespaces=namespaces)
        
        for stat in statistics:
            code = stat.xpath("efbc:StatisticsCode/text()", namespaces=namespaces)
            value = stat.xpath("efbc:StatisticsNumeric/text()", namespaces=namespaces)
            
            if lot_id and code and value and code[0] == 'complainants':
                result.append({
                    "relatedLot": lot_id[0],
                    "value": int(value[0]),
                    "measure": "complainants",
                    "scope": "complaints"
                })

    return result

def merge_buyer_review_complainants(release_json, complainants_data):
    if complainants_data:
        statistics = release_json.setdefault("statistics", [])

        # Find the highest existing id
        max_id = max([int(stat.get("id", 0)) for stat in statistics], default=0)

        for data in complainants_data:
            max_id += 1
            statistic = {
                "id": str(max_id),
                "value": data["value"],
                "measure": data["measure"],
                "scope": data["scope"],
                "relatedLot": data["relatedLot"]
            }
            statistics.append(statistic)

        # Ensure the lot exists in tender.lots
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])
        for data in complainants_data:
            if not any(lot.get("id") == data["relatedLot"] for lot in lots):
                lots.append({"id": data["relatedLot"]})

    return release_json