#converters/BT_193.py
from lxml import etree

def parse_tender_variant(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"bids": {"details": []}}

    lot_tenders = root.xpath("//efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        variant_indicator = lot_tender.xpath("efbc:TenderVariantIndicator/text()", namespaces=namespaces)
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
        
        bid = {
            "id": tender_id,
            "relatedLots": [lot_id]
        }
        
        if variant_indicator:
            bid["variant"] = variant_indicator[0].lower() == 'true'
        
        result["bids"]["details"].append(bid)

    return result if result["bids"]["details"] else None