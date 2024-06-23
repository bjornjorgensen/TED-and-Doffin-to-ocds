# converters/BT_553_Tender.py
from lxml import etree

def parse_subcontracting_value(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = []

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        subcontracting_value = lot_tender.xpath("efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermAmount/text()", namespaces=namespaces)
        currency = lot_tender.xpath("efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermAmount/@currencyID", namespaces=namespaces)

        if tender_id and lot_id and subcontracting_value and currency:
            result.append({
                "id": tender_id[0],
                "relatedLots": [lot_id[0]],
                "subcontracting": {
                    "value": {
                        "amount": float(subcontracting_value[0]),
                        "currency": currency[0]
                    }
                }
            })

    return result if result else None

def merge_subcontracting_value(release_json, subcontracting_data):
    if subcontracting_data:
        bids = release_json.setdefault("bids", {})
        details = bids.setdefault("details", [])

        for data in subcontracting_data:
            bid = next((b for b in details if b.get("id") == data["id"]), None)
            if not bid:
                bid = {"id": data["id"]}
                details.append(bid)
            
            bid["relatedLots"] = data["relatedLots"]
            bid["subcontracting"] = data["subcontracting"]

    return release_json