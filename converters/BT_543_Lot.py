# converters/BT_543_Lot.py
from lxml import etree

def parse_award_criteria_complicated_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        calculation_expression = lot.xpath(".//cac:AwardingTerms/cac:AwardingCriterion/cbc:CalculationExpression/text()", namespaces=namespaces)
        
        if calculation_expression:
            result[lot_id] = calculation_expression[0]

    return result if result else None

def merge_award_criteria_complicated_lot(release_json, complicated_data):
    if complicated_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, weighting_description in complicated_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            award_criteria = lot.setdefault("awardCriteria", {})
            award_criteria["weightingDescription"] = weighting_description

    return release_json