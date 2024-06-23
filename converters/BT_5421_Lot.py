# converters/BT_5421_Lot.py
from lxml import etree

def parse_award_criterion_number_weight_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    weight_mapping = {
        'dec-exa': 'decimalExact',
        'dec-mid': 'decimalRangeMiddle',
        'ord-imp': 'order',
        'per-exa': 'percentageExact',
        'per-mid': 'percentageRangeMiddle',
        'poi-exa': 'pointsExact',
        'poi-mid': 'pointsRangeMiddle'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//cac:SubordinateAwardingCriterion", namespaces=namespaces)
        
        if criteria:
            result[lot_id] = []
            for criterion in criteria:
                weight_codes = criterion.xpath(".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efbc:ParameterCode/text()", namespaces=namespaces)
                for code in weight_codes:
                    if code in weight_mapping:
                        result[lot_id].append(weight_mapping[code])

    return result if result else None

def merge_award_criterion_number_weight_lot(release_json, weight_data):
    if weight_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, weights in weight_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            award_criteria = lot.setdefault("awardCriteria", {})
            criteria = award_criteria.setdefault("criteria", [])

            for weight in weights:
                criterion = next((c for c in criteria if "numbers" not in c or not any(n.get("weight") == weight for n in c["numbers"])), None)
                if not criterion:
                    criterion = {}
                    criteria.append(criterion)
                
                numbers = criterion.setdefault("numbers", [])
                if not any(n.get("weight") == weight for n in numbers):
                    numbers.append({"weight": weight})

    return release_json