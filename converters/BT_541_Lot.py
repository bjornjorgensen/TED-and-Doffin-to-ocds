# converters/BT_541_Lot.py
from lxml import etree

def parse_award_criterion_numbers_lot(xml_content):
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

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//cac:SubordinateAwardingCriterion", namespaces=namespaces)
        
        if criteria:
            result[lot_id] = []
            for criterion in criteria:
                criterion_numbers = []
                for param_type in ['number-fixed', 'number-threshold', 'number-weight']:
                    number = criterion.xpath(f".//efac:AwardCriterionParameter[efbc:ParameterCode/@listName='{param_type}']/efbc:ParameterNumeric/text()", namespaces=namespaces)
                    if number:
                        criterion_numbers.append({"type": param_type, "number": float(number[0])})
                if criterion_numbers:
                    result[lot_id].append(criterion_numbers)

    return result if result else None

def merge_award_criterion_numbers_lot(release_json, criterion_data):
    if criterion_data:
        tender = release_json.setdefault("tender", {})
        lots = tender.setdefault("lots", [])

        for lot_id, criteria_numbers in criterion_data.items():
            lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
            if not lot:
                lot = {"id": lot_id}
                lots.append(lot)
            
            award_criteria = lot.setdefault("awardCriteria", {})
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