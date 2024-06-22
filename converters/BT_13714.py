from lxml import etree

def parse_tender_lot_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    bids = []
    lot_tenders = root.xpath("//efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        bid_id_elements = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)
        lot_id_elements = lot_tender.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)
        
        if bid_id_elements and lot_id_elements:
            bid_id = bid_id_elements[0]
            lot_id = lot_id_elements[0]
            
            bid = next((b for b in bids if b["id"] == bid_id), None)
            if bid is None:
                bid = {"id": bid_id, "relatedLots": []}
                bids.append(bid)
            
            if lot_id not in bid["relatedLots"]:
                bid["relatedLots"].append(lot_id)

    return {"bids": {"details": bids}} if bids else None