# converters/BT_633_Organization_Natural_Person.py
from lxml import etree

def parse_organization_natural_person(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}

    organization_elements = root.xpath("//efac:Organization", namespaces=namespaces)
    for org in organization_elements:
        org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        natural_person_indicator = org.xpath("efbc:NaturalPersonIndicator/text()", namespaces=namespaces)
        
        if org_id and natural_person_indicator:
            result[org_id[0]] = natural_person_indicator[0].lower() == 'true'

    return result

def merge_organization_natural_person(release_json, natural_person_data):
    if natural_person_data:
        parties = release_json.setdefault("parties", [])

        for org_id, is_natural_person in natural_person_data.items():
            party = next((p for p in parties if p.get("id") == org_id), None)
            if not party:
                party = {"id": org_id}
                parties.append(party)
            
            details = party.setdefault("details", {})
            if is_natural_person:
                details["scale"] = "selfEmployed"
            elif "scale" in details and details["scale"] == "selfEmployed":
                del details["scale"]

    return release_json