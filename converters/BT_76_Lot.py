# converters/BT_76_Lot.py

from lxml import etree

def parse_tenderer_legal_form(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        legal_form = lot.xpath("cac:TenderingTerms/cac:TendererQualificationRequest[not(cac:SpecificTendererRequirement)]/cbc:CompanyLegalForm/text()", namespaces=namespaces)

        if legal_form:
            result[lot_id] = legal_form[0]

    return result

def merge_tenderer_legal_form(release_json, legal_form_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, legal_form in legal_form_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)

        contract_terms = lot.setdefault("contractTerms", {})
        contract_terms["tendererLegalForm"] = legal_form

    return release_json