# converters/BT_760_LotResult.py

from lxml import etree

def parse_received_submissions_type(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    submission_type_mapping = {
        'part-req': 'requests',
        't-esubm': 'electronicBids',
        't-med': 'mediumBids',
        't-micro': 'microBids',
        't-no-eea': 'foreignBidsFromNonEU',
        't-no-verif': '',
        't-oth-eea': 'foreignBidsFromEU',
        't-small': 'smallBids',
        't-sme': 'smeBids',
        't-verif-inad': 'disqualifiedBids',
        't-verif-inad-low': 'tendersAbnormallyLow',
        'tenders': 'bids'
    }

    result = []
    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)

    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        submission_types = lot_result.xpath("efac:ReceivedSubmissionsStatistics/efbc:StatisticsCode[@listName='received-submission-type']/text()", namespaces=namespaces)

        for submission_type in submission_types:
            if lot_id and submission_type in submission_type_mapping:
                result.append({
                    'lotId': lot_id[0],
                    'measure': submission_type_mapping[submission_type]
                })

    return result

def merge_received_submissions_type(release_json, submissions_type_data):
    bids = release_json.setdefault("bids", {})
    statistics = bids.setdefault("statistics", [])

    # Find the highest existing id
    max_id = max([int(stat.get("id", 0)) for stat in statistics]) if statistics else 0

    for submission in submissions_type_data:
        max_id += 1
        statistics.append({
            "id": str(max_id),
            "measure": submission['measure'],
            "relatedLot": submission['lotId']
        })

    return release_json