# converters/BT_540_Lot.py
from lxml import etree

def parse_award_criterion_description_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//cac:SubordinateAwardingCriterion", namespaces=namespaces)
        
        if criteria:
            result[lot_id] = []
            for criterion in criteria:
                description = criterion.xpath("cbc:Description/text()", namespaces=namespaces)
                if description:
                    result[lot_id].append(description[0])

    return result if result else None

def merge_award_criterion_description_lot(release_json, criterion_data):
    if criterion_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, descriptions in criterion_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            award_criteria = lot.setdefault("awardCriteria", {})
            criteria = award_criteria.setdefault("criteria", [])

            for description in descriptions:
                criterion = next((c for c in criteria if "description" not in c), None)
                if criterion:
                    criterion["description"] = description
                else:
                    criteria.append({"description": description})

    return release_json