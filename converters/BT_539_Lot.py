# converters/BT_539_Lot.py
from lxml import etree

def parse_award_criterion_type_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criterion_types = lot.xpath(".//cac:SubordinateAwardingCriterion/cbc:AwardingCriterionTypeCode[@listName='award-criterion-type']/text()", namespaces=namespaces)
        
        if criterion_types:
            result[lot_id] = criterion_types

    return result if result else None

def merge_award_criterion_type_lot(release_json, criterion_data):
    if criterion_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, criterion_types in criterion_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            award_criteria = lot.setdefault("awardCriteria", {})
            criteria = award_criteria.setdefault("criteria", [])

            for criterion_type in criterion_types:
                criterion = next((c for c in criteria if c.get("type") == criterion_type), None)
                if not criterion:
                    criteria.append({"type": criterion_type})

    return release_json