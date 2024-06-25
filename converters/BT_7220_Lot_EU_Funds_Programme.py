# converters/BT_7220_Lot_EU_Funds_Programme.py
from lxml import etree

def parse_lot_eu_funds_programme(xml_content):
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
        funding_programmes = lot.xpath(".//efac:Funding/cbc:FundingProgramCode[@listName='eu-programme']/text()", namespaces=namespaces)
        
        if funding_programmes:
            result[lot_id] = funding_programmes

    return result

def merge_lot_eu_funds_programme(release_json, eu_funds_data):
    if eu_funds_data:
        planning = release_json.setdefault("planning", {})
        budget = planning.setdefault("budget", {})
        finance = budget.setdefault("finance", [])

        for lot_id, programmes in eu_funds_data.items():
            existing_finance = [f for f in finance if f.get("relatedLot") == lot_id]
            
            for index, programme in enumerate(programmes, start=1):
                if existing_finance:
                    # Update existing finance object
                    finance_obj = existing_finance[index - 1] if index <= len(existing_finance) else None
                    if finance_obj:
                        finance_obj["title"] = programme
                    else:
                        finance.append({
                            "id": str(len(finance) + 1),
                            "title": programme,
                            "relatedLot": lot_id
                        })
                else:
                    # Create new finance object
                    finance.append({
                        "id": str(len(finance) + 1),
                        "title": programme,
                        "relatedLot": lot_id
                    })

    return release_json