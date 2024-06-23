# converters/BT_508.py
from lxml import etree

def parse_buyer_profile_url(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"parties": []}

    contracting_party_elements = root.xpath("//cac:ContractingParty", namespaces=namespaces)
    
    for contracting_party in contracting_party_elements:
        buyer_profile_uri = contracting_party.xpath("cbc:BuyerProfileURI/text()", namespaces=namespaces)
        party_id = contracting_party.xpath("cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        
        if buyer_profile_uri and party_id:
            party = {
                "id": party_id[0],
                "details": {
                    "buyerProfile": buyer_profile_uri[0]
                },
                "roles": ["buyer"]
            }
            result["parties"].append(party)

    return result if result["parties"] else None

def merge_buyer_profile_url(release_json, buyer_profile_data):
    if buyer_profile_data and "parties" in buyer_profile_data:
        existing_parties = release_json.setdefault("parties", [])
        
        for new_party in buyer_profile_data["parties"]:
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                # Update existing party
                existing_party.setdefault("details", {})["buyerProfile"] = new_party["details"]["buyerProfile"]
                if "buyer" not in existing_party.setdefault("roles", []):
                    existing_party["roles"].append("buyer")
            else:
                # Add new party
                existing_parties.append(new_party)
