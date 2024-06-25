# converters/BT_767_Lot.py

from lxml import etree

def parse_electronic_auction(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        auction_indicator = lot.xpath("cac:TenderingProcess/cac:AuctionTerms/cbc:AuctionConstraintIndicator/text()", namespaces=namespaces)
        
        if auction_indicator and auction_indicator[0].lower() == 'true':
            result[lot_id] = True

    return result

def merge_electronic_auction(release_json, auction_data):
    if not auction_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, has_auction in auction_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        techniques = lot.setdefault("techniques", {})
        techniques["hasElectronicAuction"] = has_auction

    return release_json