# converters/opt_300_parser.py
from lxml import etree
import json

def parse_opt_300(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {
        "parties": [],
        "awards": [],
        "buyer": {}
    }

    # OPT-300-Contract-Signatory
    signatory_ids = root.xpath("//efac:NoticeResult/efac:SettledContract/cac:SignatoryParty/cac:PartyIdentification/cbc:ID", namespaces=namespaces)
    for signatory_id in signatory_ids:
        org_id = signatory_id.text
        org = next((party for party in result["parties"] if party["id"] == org_id), None)
        if not org:
            org = {"id": org_id, "roles": ["buyer"]}
            result["parties"].append(org)
        
        org_name = root.xpath(f"//efac:Organizations/efac:Organization/efac:Company[cac:PartyIdentification/cbc:ID='{org_id}']/cac:PartyName/cbc:Name", namespaces=namespaces)
        if org_name:
            org["name"] = org_name[0].text

        # Add buyer to awards
        contract = root.xpath(f"//efac:NoticeResult/efac:SettledContract[cac:SignatoryParty/cac:PartyIdentification/cbc:ID='{org_id}']", namespaces=namespaces)
        if contract:
            award = {"buyers": [{"id": org_id}]}
            result["awards"].append(award)

    # OPT-300-Procedure-Buyer
    buyer_ids = root.xpath("//cac:ContractingParty/cac:Party/cac:PartyIdentification/cbc:ID", namespaces=namespaces)
    for buyer_id in buyer_ids:
        org_id = buyer_id.text
        org = next((party for party in result["parties"] if party["id"] == org_id), None)
        if not org:
            org = {"id": org_id, "roles": ["buyer"]}
            result["parties"].append(org)
        elif "buyer" not in org["roles"]:
            org["roles"].append("buyer")
        
        result["buyer"]["id"] = org_id

    # OPT-300-Procedure-SProvider
    sprovider_ids = root.xpath("//cac:ContractingParty/cac:Party/cac:ServiceProviderParty/cac:Party/cac:PartyIdentification/cbc:ID", namespaces=namespaces)
    for sprovider_id in sprovider_ids:
        org_id = sprovider_id.text
        org = next((party for party in result["parties"] if party["id"] == org_id), None)
        if not org:
            org = {"id": org_id}
            result["parties"].append(org)
        
        org_name = root.xpath(f"//efac:Organizations/efac:Organization/efac:Company[cac:PartyIdentification/cbc:ID='{org_id}']/cac:PartyName/cbc:Name", namespaces=namespaces)
        if org_name:
            org["name"] = org_name[0].text

    return result

def merge_opt_300(release, parsed_data):
    # Merge parties
    for new_party in parsed_data["parties"]:
        existing_party = next((party for party in release.get("parties", []) if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.update(new_party)
        else:
            release.setdefault("parties", []).append(new_party)

    # Merge awards
    for new_award in parsed_data["awards"]:
        release.setdefault("awards", []).append(new_award)

    # Merge buyer
    if "buyer" not in release and parsed_data["buyer"]:
        release["buyer"] = parsed_data["buyer"]

