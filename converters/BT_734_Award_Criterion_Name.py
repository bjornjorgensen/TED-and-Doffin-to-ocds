# converters/BT_734_Award_Criterion_Name.py
from lxml import etree

def parse_award_criterion_name(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {
        'lots': {},
        'lotGroups': {}
    }

    # Process Lots
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/cbc:Name/text()", namespaces=namespaces)
        if criteria:
            result['lots'][lot_id] = criteria

    # Process Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup in lotgroup_elements:
        lotgroup_id = lotgroup.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lotgroup.xpath(".//cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/cbc:Name/text()", namespaces=namespaces)
        if criteria:
            result['lotGroups'][lotgroup_id] = criteria

    return result

def merge_award_criterion_name(release_json, criterion_name_data):
    if criterion_name_data:
        tender = release_json.setdefault("tender", {})

        # Merge Lots
        lots = tender.setdefault("lots", [])
        for lot_id, criteria_names in criterion_name_data['lots'].items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            award_criteria = lot.setdefault("awardCriteria", {})
            criteria = award_criteria.setdefault("criteria", [])
            
            for i, name in enumerate(criteria_names):
                if i < len(criteria):
                    criteria[i]["name"] = name
                else:
                    criteria.append({"name": name})

        # Merge Lot Groups
        lot_groups = tender.setdefault("lotGroups", [])
        for lotgroup_id, criteria_names in criterion_name_data['lotGroups'].items():
            lotgroup = next((lg for lg in lot_groups if lg.get("id") == lotgroup_id), None)
            if not lotgroup:
                lotgroup = {"id": lotgroup_id}
                lot_groups.append(lotgroup)
            award_criteria = lotgroup.setdefault("awardCriteria", {})
            criteria = award_criteria.setdefault("criteria", [])
            
            for i, name in enumerate(criteria_names):
                if i < len(criteria):
                    criteria[i]["name"] = name
                else:
                    criteria.append({"name": name})

    return release_json