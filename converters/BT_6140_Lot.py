# converters/BT_6140_Lot.py
from lxml import etree

def parse_lot_eu_funds_details(xml_content):
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
        funding_descriptions = lot.xpath(".//efac:Funding/cbc:Description/text()", namespaces=namespaces)
        
        if funding_descriptions:
            result[lot_id] = funding_descriptions

    return result

def merge_lot_eu_funds_details(release_json, lot_data):
    if lot_data:
        planning = release_json.setdefault("planning", {})
        budget = planning.setdefault("budget", {})
        finance = budget.setdefault("finance", [])

        for lot_id, descriptions in lot_data.items():
            for index, description in enumerate(descriptions, start=1):
                existing_finance = next((f for f in finance if f.get("description") == description), None)
                if not existing_finance:
                    new_finance = {
                        "id": str(len(finance) + 1),
                        "description": description
                    }
                    finance.append(new_finance)

    return release_json