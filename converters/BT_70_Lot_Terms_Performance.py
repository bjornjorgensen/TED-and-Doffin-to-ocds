# converters/BT_70_Lot_Terms_Performance.py
from lxml import etree

def parse_terms_performance(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        performance_terms = lot.xpath(".//cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='conditions']/cbc:Description/text()", namespaces=namespaces)
        
        if performance_terms:
            result[lot_id] = performance_terms[0]

    return result

def merge_terms_performance(release_json, terms_performance_data):
    if terms_performance_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, performance_terms in terms_performance_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            contract_terms = lot.setdefault("contractTerms", {})
            contract_terms["performanceTerms"] = performance_terms

    return release_json