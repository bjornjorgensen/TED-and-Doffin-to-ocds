# converters/BT_7531_Lot.py

from lxml import etree

def parse_selection_criteria_weight(xml_content):
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
        'per-exa': 'percentageExact',
        'per-ran': 'percentageRangeMiddle',
        'dec-exa': 'decimalExact',
        'dec-ran': 'decimalRangeMiddle',
        'poi-exa': 'pointsExact',
        'poi-ran': 'pointsRangeMiddle',
        'ord': 'order'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//efac:SelectionCriteria", namespaces=namespaces)
        
        lot_criteria = []
        for criterion in criteria:
            usage = criterion.xpath("cbc:CalculationExpressionCode[@listName='usage']/text()", namespaces=namespaces)
            if usage and usage[0] == 'used':
                weight_code = criterion.xpath("efac:CriterionParameter[efbc:ParameterCode/@listName='number-weight']/efbc:ParameterCode/text()", namespaces=namespaces)
                if weight_code:
                    weight = weight_mapping.get(weight_code[0])
                    if weight:
                        lot_criteria.append(weight)
        
        if lot_criteria:
            result[lot_id] = lot_criteria

    return result

def merge_selection_criteria_weight(release_json, criteria_weight_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, weights in criteria_weight_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        selection_criteria = lot.setdefault("selectionCriteria", {})
        existing_criteria = selection_criteria.setdefault("criteria", [])

        for index, weight in enumerate(weights):
            if index < len(existing_criteria):
                existing_criterion = existing_criteria[index]
            else:
                existing_criterion = {}
                existing_criteria.append(existing_criterion)

            numbers = existing_criterion.setdefault("numbers", [])
            
            weight_number = next((n for n in numbers if n.get("type") == "weight"), None)
            if weight_number:
                weight_number["weight"] = weight
            else:
                numbers.append({"type": "weight", "weight": weight})

    return release_json