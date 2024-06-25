# converters/BT_720_Tender_Value.py
from lxml import etree


def parse_tender_value(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {
        'bids': [],
        'awards': []
    }

    lot_tenders = root.xpath("//efac:LotTender", namespaces=namespaces)
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        amount = lot_tender.xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/text()", namespaces=namespaces)
        currency = lot_tender.xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/@currencyID", namespaces=namespaces)

        if tender_id and amount and currency:
            bid_data = {
                'id': tender_id[0],
                'value': {
                    'amount': float(amount[0]),
                    'currency': currency[0]
                }
            }
            if lot_id:
                bid_data['relatedLots'] = [lot_id[0]]
            result['bids'].append(bid_data)

    lot_results = root.xpath("//efac:LotResult", namespaces=namespaces)
    for lot_result in lot_results:
        result_id = lot_result.xpath("cbc:ID[@schemeName='result']/text()", namespaces=namespaces)
        tender_id = lot_result.xpath("efac:LotTender/cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)

        if result_id and tender_id:
            # Find corresponding LotTender to get the value
            lot_tender = root.xpath(f"//efac:LotTender[cbc:ID[@schemeName='tender']='{tender_id[0]}']", namespaces=namespaces)
            if lot_tender:
                amount = lot_tender[0].xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/text()", namespaces=namespaces)
                currency = lot_tender[0].xpath("cac:LegalMonetaryTotal/cbc:PayableAmount/@currencyID", namespaces=namespaces)

                if amount and currency:
                    award_data = {
                        'id': result_id[0],
                        'value': {
                            'amount': float(amount[0]),
                            'currency': currency[0]
                        }
                    }
                    if lot_id:
                        award_data['relatedLots'] = [lot_id[0]]
                    result['awards'].append(award_data)

    return result

def merge_tender_value(release_json, tender_value_data):
    if tender_value_data:
        bids = release_json.setdefault("bids", {})
        bid_details = bids.setdefault("details", [])
        awards = release_json.setdefault("awards", [])

        for bid_data in tender_value_data['bids']:
            bid = next((b for b in bid_details if b.get("id") == bid_data["id"]), None)
            if bid:
                bid.update(bid_data)
            else:
                bid_details.append(bid_data)

        for award_data in tender_value_data['awards']:
            award = next((a for a in awards if a.get("id") == award_data["id"]), None)
            if award:
                award.update(award_data)
            else:
                awards.append(award_data)

    return release_json