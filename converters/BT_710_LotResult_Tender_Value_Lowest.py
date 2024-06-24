# converters/BT_710_LotResult_Tender_Value_Lowest.py
from lxml import etree

def parse_tender_value_lowest(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = []

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        lower_tender_amount = lot_result.xpath("cbc:LowerTenderAmount/text()", namespaces=namespaces)
        currency = lot_result.xpath("cbc:LowerTenderAmount/@currencyID", namespaces=namespaces)

        if lot_id and lower_tender_amount and currency:
            result.append({
                "relatedLot": lot_id[0],
                "value": float(lower_tender_amount[0]),
                "currency": currency[0]
            })

    return result

def merge_tender_value_lowest(release_json, tender_value_data):
    if tender_value_data:
        bids = release_json.setdefault("bids", {})
        statistics = bids.setdefault("statistics", [])

        # Find the highest existing id
        max_id = max([int(stat.get("id", 0)) for stat in statistics], default=0)

        for data in tender_value_data:
            max_id += 1
            statistic = {
                "id": str(max_id),
                "measure": "lowestValidBidValue",
                "value": data["value"],
                "currency": data["currency"],
                "relatedLot": data["relatedLot"]
            }
            statistics.append(statistic)

        # Ensure the lot exists in tender.lots
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])
        for data in tender_value_data:
            if not any(lot.get("id") == data["relatedLot"] for lot in lots):
                lots.append({"id": data["relatedLot"]})

    return release_json