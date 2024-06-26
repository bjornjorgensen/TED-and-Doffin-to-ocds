# converters/BT_775_Lot.py

from lxml import etree

def parse_social_procurement(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    social_objective_mapping = {
        'acc-all': 'social.accessibility',
        'et-eq': 'social.ethnicEquality',
        'gen-eq': 'social.genderEquality',
        'hum-right': 'social.humanRightsInSupplyChain',
        'opp': 'social.disadvantagedEmploymentOpportunities',
        'other': 'social',
        'work-cond': 'social.laborRightsPromotion'
    }

    result = {}
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)

    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        objective_codes = lot.xpath("cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='social-objective']/cbc:ProcurementTypeCode/text()", namespaces=namespaces)
        
        if objective_codes:
            result[lot_id] = [social_objective_mapping.get(code, 'social') for code in objective_codes]

    return result

def merge_social_procurement(release_json, social_procurement_data):
    if not social_procurement_data:
        return release_json

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    strategies = [
        "awardCriteria",
        "contractPerformanceConditions",
        "selectionCriteria",
        "technicalSpecifications"
    ]

    for lot_id, sustainability_goals in social_procurement_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        lot["hasSustainability"] = True
        sustainability = lot.setdefault("sustainability", [])
        for goal in sustainability_goals:
            sustainability.append({
                "goal": goal,
                "strategies": strategies
            })

    return release_json