from lxml import etree

def parse_selection_criteria_type(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extension/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = []

    lots = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//efac:SelectionCriteria", namespaces=namespaces)
        
        lot_criteria = []
        for criterion in criteria:
            usage = criterion.xpath("cbc:CalculationExpressionCode[@listName='usage']/text()", namespaces=namespaces)
            if usage and usage[0] == 'used':
                criterion_type = criterion.xpath("cbc:CriterionTypeCode[@listName='selection-criterion']/text()", namespaces=namespaces)
                if criterion_type:
                    lot_criteria.append(criterion_type[0])
        
        if lot_criteria:
            result.append({
                'id': lot_id,
                'criteria': lot_criteria
            })

    return result

def merge_selection_criteria_type(release_json, criteria_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    criterion_type_mapping = {
        'ef-stand': 'economic',
        'other': 'other',
        'sui-act': 'suitability',
        'tp-abil': 'technical'
    }

    for lot_criteria in criteria_data:
        lot = next((l for l in lots if l.get('id') == lot_criteria['id']), None)
        if not lot:
            lot = {'id': lot_criteria['id']}
            lots.append(lot)

        selection_criteria = lot.setdefault('selectionCriteria', {})
        criteria = selection_criteria.setdefault('criteria', [])

        for criterion_type in lot_criteria['criteria']:
            mapped_type = criterion_type_mapping.get(criterion_type, 'other')
            criterion = next((c for c in criteria if c.get('type') == mapped_type), None)
            if not criterion:
                criterion = {'type': mapped_type}
                criteria.append(criterion)

    return release_json