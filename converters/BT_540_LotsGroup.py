# converters/BT_540_LotsGroup.py
from lxml import etree

def parse_award_criterion_description_lots_group(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lots_group_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lots_group in lots_group_elements:
        group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lots_group.xpath(".//cac:SubordinateAwardingCriterion", namespaces=namespaces)
        
        if criteria:
            result[group_id] = []
            for criterion in criteria:
                description = criterion.xpath("cbc:Description/text()", namespaces=namespaces)
                if description:
                    result[group_id].append(description[0])

    return result if result else None

def merge_award_criterion_description_lots_group(release_json, criterion_data):
    if criterion_data:
        tender = release_json.setdefault("tender", {})
        lot_groups = tender.setdefault("lotGroups", [])

        for group_id, descriptions in criterion_data.items():
            lot_group = next((group for group in lot_groups if group.get("id") == group_id), None)
            if not lot_group:
                lot_group = {"id": group_id}
                lot_groups.append(lot_group)
            
            award_criteria = lot_group.setdefault("awardCriteria", {})
            criteria = award_criteria.setdefault("criteria", [])

            for description in descriptions:
                criterion = next((c for c in criteria if "description" not in c), None)
                if criterion:
                    criterion["description"] = description
                else:
                    criteria.append({"description": description})

    return release_json