# converters/BT_500.py
from lxml import etree

def parse_organization_info(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    for org in organizations:
        # Company
        company = org.xpath("efac:Company", namespaces=namespaces)
        if company:
            org_id = company[0].xpath("cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
            org_name = company[0].xpath("cac:PartyName/cbc:Name/text()", namespaces=namespaces)
            if org_id and org_name:
                result["parties"].append({
                    "id": org_id[0],
                    "name": org_name[0]
                })

        # TouchPoint
        touchpoint = org.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            tp_id = touchpoint[0].xpath("cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()", namespaces=namespaces)
            tp_name = touchpoint[0].xpath("cac:PartyName/cbc:Name/text()", namespaces=namespaces)
            company_id = org.xpath("efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
            if tp_id and tp_name:
                party = {
                    "id": tp_id[0],
                    "name": tp_name[0]
                }
                if company_id:
                    party["identifier"] = {
                        "id": company_id[0],
                        "scheme": "internal"
                    }
                result["parties"].append(party)

    # UBO
    ubos = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubos:
        ubo_id = ubo.xpath("cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)
        ubo_name = ubo.xpath("cbc:FamilyName/text()", namespaces=namespaces)
        if ubo_id and ubo_name:
            # Find the associated organization
            org_id = root.xpath("//efac:Organizations/efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
            if org_id:
                org = next((party for party in result["parties"] if party.get("id") == org_id[0]), None)
                if org:
                    if "beneficialOwners" not in org:
                        org["beneficialOwners"] = []
                    org["beneficialOwners"].append({
                        "id": ubo_id[0],
                        "name": ubo_name[0]
                    })

    return result

def merge_organization_info(release_json, organization_info_data):
    if not organization_info_data or "parties" not in organization_info_data:
        return release_json

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_info_data["parties"]:
        if "id" not in new_party:
            continue  # Skip parties without an ID

        existing_party = next((party for party in existing_parties if party.get("id") == new_party["id"]), None)
        if existing_party:
            existing_party.update(new_party)
        else:
            existing_parties.append(new_party)

    return release_json