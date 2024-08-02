# converters/BT_10.py
from lxml import etree

def parse_contract_xml(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    parties = []
    authority_table = {
        "airport": ("COFOG", "Airport-related activities", "04.7"),
        "defence": ("COFOG", "Defence", "02"),
        "econ-aff": ("COFOG", "Economic affairs", "04"),
        "education": ("COFOG", "Education", "09"),
        "electricity": ("COFOG", "Electricity-related activities", "04.3"),
        "env-pro": ("COFOG", "Environmental protection", "05"),
        "gas-heat": ("COFOG", "Production, transport or distribution of gas or heat", "04.3"),
        "gas-oil": ("COFOG", "Extraction of gas or oil", "04.4"),
        "gen-pub": ("COFOG", "General public services", "01"),
        "hc-am": ("COFOG", "Housing and community amenities", "06"),
        "health": ("COFOG", "Health", "07"),
        "port": ("COFOG", "Port-related activities", "04.5"),
        "post": ("COFOG", "Postal services", "04.6"),
        "pub-os": ("COFOG", "Public order and safety", "03"),
        "rail": ("COFOG", "Railway services", "04.5"),
        "rcr": ("COFOG", "Recreation, culture and religion", "08"),
        "soc-pro": ("COFOG", "Social protection", "10"),
        "solid-fuel": ("COFOG", "Exploration or extraction of coal or other solid fuels", "04.4"),
        "urttb": ("COFOG", "Urban railway, tramway, trolleybus or bus services", "04.5"),
        "water": ("COFOG", "Water-related activities", "06.3")
    }

    contracting_party_xpath = "//cac:ContractingParty"
    party_id_xpath = ".//cac:PartyIdentification/cbc:ID"
    activity_type_code_xpath = ".//cbc:ActivityTypeCode[@listName='authority-activity']"
    
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    for contracting_party in root.xpath(contracting_party_xpath, namespaces=namespaces):
        party_id_elements = contracting_party.xpath(party_id_xpath, namespaces=namespaces)
        if not party_id_elements:
            continue  # Skip this contracting party if it doesn't have an ID

        party_id = party_id_elements[0].text
        
        activity_type_code_elements = contracting_party.xpath(activity_type_code_xpath, namespaces=namespaces)
        if not activity_type_code_elements:
            continue  # Skip this contracting party if it doesn't have an activity type code

        activity_type_code = activity_type_code_elements[0].text

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
        
        if activity_type_code in authority_table:
            scheme, description, cofog_id = authority_table[activity_type_code]
            classification = {
                "scheme": scheme,
                "id": cofog_id,
                "description": description
            }
        else:
            classification = {
                "scheme": "eu-main-activity",
                "id": activity_type_code,
                "description": activity_type_code
            }
        
        organization['details']['classifications'].append(classification)

    return {"parties": parties}
