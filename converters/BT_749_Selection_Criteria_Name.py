from lxml import etree

def parse_selection_criteria_name(xml_content):
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
                name = criterion.xpath("cbc:Name/text()", namespaces=namespaces)
                description = criterion.xpath("cbc:Description/text()", namespaces=namespaces)
                if name:
                    lot_criteria.append({
                        'name': name[0],
                        'description': description[0] if description else ''
                    })
        
        if lot_criteria:
            result.append({
                'id': lot_id,
                'criteria': lot_criteria
            })

    return result

def merge_selection_criteria_name(release_json, criteria_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_criteria in criteria_data:
        lot = next((l for l in lots if l.get('id') == lot_criteria['id']), None)
        if not lot:
            lot = {'id': lot_criteria['id']}
            lots.append(lot)

        selection_criteria = lot.setdefault('selectionCriteria', {})
        criteria = selection_criteria.setdefault('criteria', [])

        for criterion in lot_criteria['criteria']:
            existing_criterion = next((c for c in criteria if c.get('description', '').startswith(criterion['name'])), None)
            if existing_criterion:
                existing_criterion['description'] = f"{criterion['name']} {criterion['description']}".strip()
            else:
                criteria.append({
                    'description': f"{criterion['name']} {criterion['description']}".strip()
                })

    return release_json