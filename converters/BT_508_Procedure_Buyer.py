# converters/BT_508_Procedure_Buyer.py

from lxml import etree

def parse_buyer_profile_url(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=namespaces)
    
    for party in contracting_parties:
        buyer_profile_uri = party.xpath("cbc:BuyerProfileURI/text()", namespaces=namespaces)
        org_id = party.xpath("cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        
        if buyer_profile_uri and org_id:
            result["parties"].append({
                "id": org_id[0],
                "details": {
                    "buyerProfile": buyer_profile_uri[0]
                },
                "roles": ["buyer"]
            })

    return result if result["parties"] else None

def merge_buyer_profile_url(release_json, buyer_profile_data):
    if not buyer_profile_data:
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in buyer_profile_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("details", {})["buyerProfile"] = new_party["details"]["buyerProfile"]
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
        else:
            existing_parties.append(new_party)