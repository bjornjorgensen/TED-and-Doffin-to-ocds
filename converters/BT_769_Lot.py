# converters/BT_769_Lot.py

from lxml import etree

def parse_multiple_tenders(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        multiple_tenders_code = lot.xpath("cac:TenderingTerms/cbc:MultipleTendersCode[@listName='permission']/text()", namespaces=namespaces)
        
        if multiple_tenders_code:
            result[lot_id] = multiple_tenders_code[0] == 'allowed'

    return result

def merge_multiple_tenders(release_json, multiple_tenders_data):
    if not multiple_tenders_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, is_allowed in multiple_tenders_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        submission_terms = lot.setdefault("submissionTerms", {})
        submission_terms["multipleBidsAllowed"] = is_allowed

    return release_json