# converters/BT_75_Lot.py

from lxml import etree

def parse_guarantee_required_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        description = lot.xpath("cac:TenderingTerms/cac:RequiredFinancialGuarantee/cbc:Description/text()", namespaces=namespaces)
        
        if description:
            result[lot_id] = description[0]

    return result

def merge_guarantee_required_description(release_json, guarantee_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, description in guarantee_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        submission_terms = lot.setdefault("submissionTerms", {})
        submission_terms["depositsGuarantees"] = description

    return release_json