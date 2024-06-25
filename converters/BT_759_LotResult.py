# converters/BT_759_LotResult.py

from lxml import etree

def parse_received_submissions_count(xml_content):
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
        submissions_count = lot_result.xpath("efac:ReceivedSubmissionsStatistics/efbc:StatisticsNumeric/text()", namespaces=namespaces)

        if lot_id and submissions_count:
            result.append({
                'lotId': lot_id[0],
                'count': int(submissions_count[0])
            })

    return result

def merge_received_submissions_count(release_json, submissions_data):
    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    # Find the highest existing id
    max_id = max([int(stat.get("id", 0)) for stat in statistics]) if statistics else 0

    for submission in submissions_data:
        max_id += 1
        statistics.append({
            "id": str(max_id),
            "value": submission['count'],
            "relatedLot": submission['lotId'],
            "measure": "receivedSubmissions"
        })

    return release_json