from lxml import etree

def parse_tender_rank(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        rank = lot_tender.xpath("cbc:RankCode/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
        
        bid = {
            "id": tender_id,
            "relatedLots": [lot_id]
        }
        
        if rank:
            bid["rank"] = int(rank[0])
        
        result["bids"]["details"].append(bid)

    return result if result["bids"]["details"] else None