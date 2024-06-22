# converters/BT_3201.py
from lxml import etree

def parse_tender_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"bids": {"details": []}}
    
    lot_tenders = root.xpath("/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender", namespaces=namespaces)
    
    for lot_tender in lot_tenders:
        tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        lot_id = lot_tender.xpath("efac:TenderLot/cbc:ID/text()", namespaces=namespaces)[0]
        tender_reference = lot_tender.xpath("efac:TenderReference/cbc:ID/text()", namespaces=namespaces)
        
        bid = {
            "id": tender_id,
            "relatedLots": [lot_id],
            "identifiers": []
        }
        
        if tender_reference:
            # Assuming the scheme is always 'NL-TENDERNL' for this example
            # In a real-world scenario, you might need to determine the correct scheme based on additional information
            bid["identifiers"].append({
                "id": tender_reference[0],
                "scheme": "NL-TENDERNL"
            })
        
        result["bids"]["details"].append(bid)
    
    return result if result["bids"]["details"] else None

def merge_tender_identifier(release_json, tender_identifier_data):
    if tender_identifier_data and "bids" in tender_identifier_data and "details" in tender_identifier_data["bids"]:
        existing_bids = release_json.setdefault("bids", {}).setdefault("details", [])
        for new_bid in tender_identifier_data["bids"]["details"]:
            existing_bid = next((bid for bid in existing_bids if bid["id"] == new_bid["id"]), None)
            if existing_bid:
                existing_bid.setdefault("identifiers", []).extend(new_bid["identifiers"])
                existing_bid.setdefault("relatedLots", []).extend(lot for lot in new_bid["relatedLots"] if lot not in existing_bid["relatedLots"])
            else:
                existing_bids.append(new_bid)
