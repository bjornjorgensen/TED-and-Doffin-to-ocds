# converters/BT_733_Award_Criteria_Order_Justification.py
from lxml import etree

def parse_award_criteria_order_justification(xml_content):
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
        justification = lot.xpath(".//cac:AwardingTerms/cac:AwardingCriterion/cbc:Description/text()", namespaces=namespaces)
        if justification:
            result['lots'][lot_id] = justification[0]

    # Process Lot Groups
    lotgroup_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lotgroup in lotgroup_elements:
        lotgroup_id = lotgroup.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        justification = lotgroup.xpath(".//cac:AwardingTerms/cac:AwardingCriterion/cbc:Description/text()", namespaces=namespaces)
        if justification:
            result['lotGroups'][lotgroup_id] = justification[0]

    return result

def merge_award_criteria_order_justification(release_json, justification_data):
    if justification_data:
        tender = release_json.setdefault("tender", {})

        # Merge Lots
        lots = tender.setdefault("lots", [])
        for lot_id, justification in justification_data['lots'].items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            award_criteria = lot.setdefault("awardCriteria", {})
            award_criteria["orderRationale"] = justification

        # Merge Lot Groups
        lot_groups = tender.setdefault("lotGroups", [])
        for lotgroup_id, justification in justification_data['lotGroups'].items():
            lotgroup = next((lg for lg in lot_groups if lg.get("id") == lotgroup_id), None)
            if not lotgroup:
                lotgroup = {"id": lotgroup_id}
                lot_groups.append(lotgroup)
            award_criteria = lotgroup.setdefault("awardCriteria", {})
            award_criteria["orderRationale"] = justification

    return release_json