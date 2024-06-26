# converters/BT_11.py
from lxml import etree

def parse_buyer_legal_type(xml_content):
    root = etree.fromstring(xml_content)
    parties = []
    buyer_legal_type_table = {
        "body-pl": "Body governed by public law",
        "body-pl-cga": "Body governed by public law, controlled by a central government authority",
        "body-pl-la": "Body governed by public law, controlled by a local authority",
        "body-pl-ra": "Body governed by public law, controlled by a regional authority",
        "cga": "Central government authority",
        "def-cont": "Defence contractor",
        "eu-ins-bod-ag": "EU institution, body or agency",
        "eu-int-org": "European Institution/Agency or International Organisation",
        "grp-p-aut": "Group of public authorities",
        "int-org": "International organisation",
        "la": "Local authority",
        "org-sub": "Organisation awarding a contract subsidised by a contracting authority",
        "org-sub-cga": "Organisation awarding a contract subsidised by a central government authority",
        "org-sub-la": "Organisation awarding a contract subsidised by a local authority",
        "org-sub-ra": "Organisation awarding a contract subsidised by a regional authority",
        "pub-undert": "Public undertaking",
        "pub-undert-cga": "Public undertaking, controlled by a central government authority",
        "pub-undert-la": "Public undertaking, controlled by a local authority",
        "pub-undert-ra": "Public undertaking, controlled by a regional authority",
        "ra": "Regional authority",
        "rl-aut": "Regional or local authority",
        "spec-rights-entity": "Entity with special or exclusive rights"
    }

    contracting_party_xpath = "//cac:ContractingParty"
    party_id_xpath = ".//cac:PartyIdentification/cbc:ID"
    party_type_code_xpath = ".//cac:ContractingPartyType/cbc:PartyTypeCode[@listName='buyer-legal-type']"

    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    for contracting_party in root.xpath(contracting_party_xpath, namespaces=namespaces):
        party_id_elements = contracting_party.xpath(party_id_xpath, namespaces=namespaces)
        if not party_id_elements:
            continue  # Skip this contracting party if it doesn't have an ID

        party_id = party_id_elements[0].text
        
        party_type_code_elements = contracting_party.xpath(party_type_code_xpath, namespaces=namespaces)
        if not party_type_code_elements:
            continue  # Skip this contracting party if it doesn't have a party type code

        party_type_code = party_type_code_elements[0].text

        organization = next((org for org in parties if org['id'] == party_id), None)
        if not organization:
            organization = {
                "id": party_id,
                "roles": ["buyer"],
                "details": {
                    "classifications": []
                }
            }
            parties.append(organization)

        classification = {
            "scheme": "TED_CA_TYPE",
            "id": party_type_code,
            "description": buyer_legal_type_table.get(party_type_code, party_type_code)
        }

        organization['details']['classifications'].append(classification)
    
    return {"parties": parties}
