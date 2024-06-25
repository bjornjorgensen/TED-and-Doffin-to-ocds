# converters/BT_765_Framework_Agreement.py

from lxml import etree

def parse_framework_agreement(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    method_mapping = {
        'fa-mix': 'withAndWithoutReopeningCompetition',
        'fa-w-rc': 'withReopeningCompetition',
        'fa-wo-rc': 'withoutReopeningCompetition'
    }

    result = {
        'lots': {},
        'part': None
    }

    # Parse for Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        fa_code = lot.xpath("cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='framework-agreement']/cbc:ContractingSystemTypeCode/text()", namespaces=namespaces)
        
        if fa_code and fa_code[0] != 'none':
            result['lots'][lot_id] = method_mapping.get(fa_code[0])

    # Parse for Part
    part_fa_code = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingProcess/cac:ContractingSystem[cbc:ContractingSystemTypeCode/@listName='framework-agreement']/cbc:ContractingSystemTypeCode/text()", namespaces=namespaces)
    
    if part_fa_code and part_fa_code[0] != 'none':
        result['part'] = method_mapping.get(part_fa_code[0])

    return result

def merge_framework_agreement(release_json, fa_data):
    tender = release_json.setdefault("tender", {})

    # Merge for Lots
    lots = tender.setdefault("lots", [])
    for lot_id, method in fa_data['lots'].items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        techniques = lot.setdefault("techniques", {})
        techniques["hasFrameworkAgreement"] = True
        techniques.setdefault("frameworkAgreement", {})["method"] = method

    # Merge for Part
    if fa_data['part']:
        techniques = tender.setdefault("techniques", {})
        techniques["hasFrameworkAgreement"] = True
        techniques.setdefault("frameworkAgreement", {})["method"] = fa_data['part']

    return release_json