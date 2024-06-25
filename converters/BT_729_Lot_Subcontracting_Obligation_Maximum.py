# converters/BT_729_Lot_Subcontracting_Obligation_Maximum.py
from lxml import etree

def parse_subcontracting_obligation_maximum(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        maximum_percent = lot.xpath(".//cac:AllowedSubcontractTerms[cbc:SubcontractingConditionsCode/@listName='subcontracting-obligation']/cbc:MaximumPercent/text()", namespaces=namespaces)
        
        if maximum_percent:
            result[lot_id] = float(maximum_percent[0]) / 100

    return result

def merge_subcontracting_obligation_maximum(release_json, subcontracting_data):
    if subcontracting_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, percentage in subcontracting_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            subcontracting_terms = lot.setdefault("subcontractingTerms", {})
            subcontracting_terms["competitiveMaximumPercentage"] = percentage

    return release_json