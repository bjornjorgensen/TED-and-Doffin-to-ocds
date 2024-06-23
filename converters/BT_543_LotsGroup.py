# converters/BT_543_LotsGroup.py
from lxml import etree

def parse_award_criteria_complicated_lots_group(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lots_group_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lots_group in lots_group_elements:
        group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        calculation_expression = lots_group.xpath(".//cac:AwardingTerms/cac:AwardingCriterion/cbc:CalculationExpression/text()", namespaces=namespaces)
        
        if calculation_expression:
            result[group_id] = calculation_expression[0]

    return result if result else None

def merge_award_criteria_complicated_lots_group(release_json, complicated_data):
    if complicated_data:
        tender = release_json.setdefault("tender", {})
        lot_groups = tender.setdefault("lotGroups", [])

        for group_id, weighting_description in complicated_data.items():
            lot_group = next((group for group in lot_groups if group.get("id") == group_id), None)
            if not lot_group:
                lot_group = {"id": group_id}
                lot_groups.append(lot_group)
            
            award_criteria = lot_group.setdefault("awardCriteria", {})
            award_criteria["weightingDescription"] = weighting_description

    return release_json