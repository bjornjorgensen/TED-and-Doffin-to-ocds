# converters/BT_7532_Lot.py

from lxml import etree

def parse_selection_criteria_threshold(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    threshold_mapping = {
        'min-score': 'minimumScore',
        'max-bids': 'maximumBids'
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
                threshold_code = criterion.xpath("efac:CriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efbc:ParameterCode/text()", namespaces=namespaces)
                if threshold_code:
                    threshold = threshold_mapping.get(threshold_code[0])
                    if threshold:
                        lot_criteria.append(threshold)
        
        if lot_criteria:
            result[lot_id] = lot_criteria

    return result

def merge_selection_criteria_threshold(release_json, criteria_threshold_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, thresholds in criteria_threshold_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        selection_criteria = lot.setdefault("selectionCriteria", {})
        existing_criteria = selection_criteria.setdefault("criteria", [])

        for index, threshold in enumerate(thresholds):
            if index < len(existing_criteria):
                existing_criterion = existing_criteria[index]
            else:
                existing_criterion = {}
                existing_criteria.append(existing_criterion)

            numbers = existing_criterion.setdefault("numbers", [])
            
            threshold_number = next((n for n in numbers if n.get("type") == "threshold"), None)
            if threshold_number:
                threshold_number["threshold"] = threshold
            else:
                numbers.append({"type": "threshold", "threshold": threshold})

    return release_json