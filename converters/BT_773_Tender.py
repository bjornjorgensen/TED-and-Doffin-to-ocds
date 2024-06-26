# converters/BT_773_Tender.py

from lxml import etree

def parse_subcontracting(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {}
    lot_tenders = root.xpath("//efac:LotTender", namespaces=namespaces)

    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID[@schemeName='tender']/text()", namespaces=namespaces)
        subcontracting_code = lot_tender.xpath("efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efbc:TermCode/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)
        
        if tender_id and subcontracting_code:
            result[tender_id[0]] = {
                'hasSubcontracting': subcontracting_code[0].lower() == 'yes',
                'relatedLots': lot_id[0] if lot_id else None
            }

    return result

def merge_subcontracting(release_json, subcontracting_data):
    if not subcontracting_data:
        return release_json

    bids = release_json.setdefault("bids", {})
    details = bids.setdefault("details", [])

    for tender_id, data in subcontracting_data.items():
        bid = next((b for b in details if b.get("id") == tender_id), None)
        if not bid:
            bid = {"id": tender_id}
            details.append(bid)
        
        bid["hasSubcontracting"] = data['hasSubcontracting']
        if data['relatedLots']:
            related_lots = bid.setdefault("relatedLots", [])
            if data['relatedLots'] not in related_lots:
                related_lots.append(data['relatedLots'])

    return release_json