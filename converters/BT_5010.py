# converters/BT_5010.py
from lxml import etree

def parse_eu_funds_financing_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }
    
    result = {
        "parties": [],
        "planning": {"budget": {"finance": []}}
    }

    # Add European Union as a party
    eu_party = {
        "id": "EU-1",  # You might want to use a more sophisticated ID generation method
        "name": "European Union",
        "roles": ["funder"]
    }
    result["parties"].append(eu_party)

    # Parse EU Funds Financing Identifier
    lot_elements = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces)
    for lot_element in lot_elements:
        lot_id = lot_element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        
        funding_elements = lot_element.xpath(
            "cac:TenderingTerms/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:Funding/efbc:FinancingIdentifier/text()",
            namespaces=namespaces
        )
        
        for funding_id in funding_elements:
            finance = {
                "id": funding_id,
                "financingParty": {
                    "id": eu_party["id"],
                    "name": eu_party["name"]
                },
                "relatedLots": [lot_id]
            }
            result["planning"]["budget"]["finance"].append(finance)

    return result if (result["parties"] and result["planning"]["budget"]["finance"]) else None

def merge_eu_funds_financing_identifier(release_json, eu_funds_data):
    if eu_funds_data:
        # Merge parties
        existing_parties = release_json.setdefault("parties", [])
        eu_party = next((party for party in eu_funds_data["parties"] if party["name"] == "European Union"), None)
        if eu_party:
            existing_eu_party = next((party for party in existing_parties if party["name"] == "European Union"), None)
            if existing_eu_party:
                existing_eu_party["roles"] = list(set(existing_eu_party.get("roles", []) + eu_party["roles"]))
            else:
                existing_parties.append(eu_party)

        # Merge finance
        if "planning" in eu_funds_data and "budget" in eu_funds_data["planning"] and "finance" in eu_funds_data["planning"]["budget"]:
            existing_finance = release_json.setdefault("planning", {}).setdefault("budget", {}).setdefault("finance", [])
            for new_finance in eu_funds_data["planning"]["budget"]["finance"]:
                existing_finance_item = next((item for item in existing_finance if item["id"] == new_finance["id"]), None)
                if existing_finance_item:
                    existing_finance_item["financingParty"] = new_finance["financingParty"]
                    existing_finance_item["relatedLots"] = list(set(existing_finance_item.get("relatedLots", []) + new_finance["relatedLots"]))
                else:
                    existing_finance.append(new_finance)
