# converters/BT_77_Lot.py

from lxml import etree

def parse_terms_financial(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        financial_terms = lot.xpath("cac:TenderingTerms/cac:PaymentTerms/cbc:Note/text()", namespaces=namespaces)
        
        if financial_terms:
            result[lot_id] = financial_terms[0]

    return result

def merge_terms_financial(release_json, financial_terms_data):
    if not financial_terms_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, terms in financial_terms_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        contract_terms = lot.setdefault("contractTerms", {})
        contract_terms["financialTerms"] = terms

    return release_json