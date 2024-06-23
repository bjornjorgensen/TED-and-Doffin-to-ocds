# converters/BT_541_LotsGroup.py
from lxml import etree

def parse_award_criterion_numbers_lots_group(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    result = {}

    lots_group_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']", namespaces=namespaces)
    for lots_group in lots_group_elements:
        group_id = lots_group.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lots_group.xpath(".//cac:SubordinateAwardingCriterion", namespaces=namespaces)
        
        if criteria:
            result[group_id] = []
            for criterion in criteria:
                criterion_numbers = []
                for param_type in ['number-fixed', 'number-threshold', 'number-weight']:
                    number = criterion.xpath(f".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='{param_type}']/efbc:ParameterNumeric/text()", namespaces=namespaces)
                    if number:
                        criterion_numbers.append({"type": param_type, "number": float(number[0])})
                if criterion_numbers:
                    result[group_id].append(criterion_numbers)

    return result if result else None

def merge_award_criterion_numbers_lots_group(release_json, criterion_data):
    if criterion_data:
        tender = release_json.setdefault("tender", {})
        lot_groups = tender.setdefault("lotGroups", [])

        for group_id, criteria_numbers in criterion_data.items():
            lot_group = next((group for group in lot_groups if group.get("id") == group_id), None)
            if not lot_group:
                lot_group = {"id": group_id}
                lot_groups.append(lot_group)
            
            award_criteria = lot_group.setdefault("awardCriteria", {})
            criteria = award_criteria.setdefault("criteria", [])

            for criterion_numbers in criteria_numbers:
                criterion = next((c for c in criteria if "numbers" not in c), None)
                if not criterion:
                    criterion = {}
                    criteria.append(criterion)
                
                numbers = criterion.setdefault("numbers", [])
                for number_data in criterion_numbers:
                    number = next((n for n in numbers if n.get("type") == number_data["type"]), None)
                    if number:
                        number["number"] = number_data["number"]
                    else:
                        numbers.append({"type": number_data["type"], "number": number_data["number"]})

    return release_json