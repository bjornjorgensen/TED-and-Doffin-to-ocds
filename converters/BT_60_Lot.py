# converters/BT_60_Lot.py
from lxml import etree

def parse_eu_funds_lot(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    eu_funded = root.xpath("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cbc:FundingProgramCode[@listName='eu-funded']/text()", namespaces=namespaces)
    
    return eu_funded[0] if eu_funded else None

def merge_eu_funds_lot(release_json, eu_funded):
    if eu_funded:
        parties = release_json.setdefault("parties", [])
        eu_party = next((party for party in parties if party.get("name") == "European Union"), None)
        
        if not eu_party:
            eu_party = {
                "id": generate_eu_id(parties),
                "name": "European Union",
                "roles": ["funder"]
            }
            parties.append(eu_party)
        elif "funder" not in eu_party.get("roles", []):
            eu_party.setdefault("roles", []).append("funder")

    return release_json

def generate_eu_id(parties):
    # This is a simple implementation. In a real-world scenario, you might want to use a more sophisticated
    # method to generate consistent IDs, possibly involving a separate register of organization identifiers.
    existing_ids = [int(party["id"]) for party in parties if party["id"].isdigit()]
    return str(max(existing_ids + [0]) + 1)