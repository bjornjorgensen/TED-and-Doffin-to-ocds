# converters/BT_610_Procedure_Buyer.py
from lxml import etree

# Mapping tables
COFOG_ACTIVITIES = [
    "gen-pub", "defence", "pub-os", "econ-aff", "env-pro", 
    "hc-am", "health", "rcr", "education", "soc-pro"
]

COFOG_MAPPING = {
    "gen-pub": ("01", "General public services"),
    "defence": ("02", "Defence"),
    "pub-os": ("03", "Public order and safety"),
    "econ-aff": ("04", "Economic affairs"),
    "env-pro": ("05", "Environmental protection"),
    "hc-am": ("06", "Housing and community amenities"),
    "health": ("07", "Health"),
    "rcr": ("08", "Recreation, culture and religion"),
    "education": ("09", "Education"),
    "soc-pro": ("10", "Social protection")
}

EU_MAIN_ACTIVITY_MAPPING = {
    "airport": "Airport-related activities",
    "defence": "Defence",
    "econ-aff": "Economic affairs",
    "education": "Education",
    "electricity": "Electricity-related activities",
    "env-pro": "Environmental protection",
    "gas-heat": "Production, transport or distribution of gas or heat",
    "gas-oil": "Extraction of gas or oil",
    "gen-pub": "General public services",
    "hc-am": "Housing and community amenities",
    "health": "Health",
    "port": "Port-related activities",
    "post": "Postal services",
    "pub-os": "Public order and safety",
    "rail": "Railway services",
    "rcr": "Recreation, culture and religion",
    "soc-pro": "Social protection",
    "solid-fuel": "Exploration or extraction of coal or other solid fuels",
    "urttb": "Urban railway, tramway, trolleybus or bus services",
    "water": "Water-related activities"
}

def parse_activity_entity(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = []
    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=namespaces)
    
    for party in contracting_parties:
        org_id = party.xpath("cac:Party/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        activity_code = party.xpath("cac:ContractingActivity/cbc:ActivityTypeCode[@listName='entity-activity']/text()", namespaces=namespaces)
        
        if org_id and activity_code:
            result.append({
                "id": org_id[0],
                "activity_code": activity_code[0]
            })

    return result

def merge_activity_entity(release_json, activity_data):
    if activity_data:
        parties = release_json.setdefault("parties", [])

        for data in activity_data:
            party = next((p for p in parties if p.get("id") == data["id"]), None)
            if not party:
                party = {"id": data["id"], "roles": ["buyer"]}
                parties.append(party)
            elif "buyer" not in party.get("roles", []):
                party.setdefault("roles", []).append("buyer")

            details = party.setdefault("details", {})
            classifications = details.setdefault("classifications", [])

            activity_code = data["activity_code"]
            if activity_code in COFOG_ACTIVITIES:
                cofog_id, cofog_description = COFOG_MAPPING[activity_code]
                classifications.append({
                    "scheme": "COFOG",
                    "id": cofog_id,
                    "description": cofog_description
                })
            else:
                classifications.append({
                    "scheme": "eu-main-activity",
                    "id": activity_code,
                    "description": EU_MAIN_ACTIVITY_MAPPING.get(activity_code, "")
                })

    return release_json