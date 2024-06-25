# converters/BT_750_Lot.py

from lxml import etree

def parse_selection_criteria_description(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {}

    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot in lot_elements:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        criteria = lot.xpath(".//efac:SelectionCriteria", namespaces=namespaces)
        
        lot_criteria = []
        for criterion in criteria:
            usage = criterion.xpath(".//cbc:CalculationExpressionCode[@listName='usage']/text()", namespaces=namespaces)
            if usage and usage[0] == 'used':
                description = criterion.xpath("cbc:Description/text()", namespaces=namespaces)
                if description:
                    lot_criteria.append(description[0])
        
        if lot_criteria:
            result[lot_id] = lot_criteria

    return result

def merge_selection_criteria_description(release_json, criteria_data):
    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_id, descriptions in criteria_data.items():
        lot = next((lot for lot in lots if lot.get("id") == lot_id), None)
        if not lot:
            lot = {"id": lot_id}
            lots.append(lot)
        
        selection_criteria = lot.setdefault("selectionCriteria", {})
        criteria = selection_criteria.setdefault("criteria", [])

        for description in descriptions:
            existing_criterion = next((c for c in criteria if c.get("description") == description), None)
            if existing_criterion:
                existing_criterion["description"] = description
            else:
                criteria.append({"description": description})

    return release_json