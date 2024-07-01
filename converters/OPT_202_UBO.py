# converters/OPT_202_UBO.py

from lxml import etree

def parse_beneficial_owner_identifier(xml_content):
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
    beneficial_owners = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner/cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)

    if organizations and beneficial_owners:
        org_id = organizations[0].xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        if org_id:
            org_id = org_id[0]
            unique_bo_ids = list(set(beneficial_owners))  # Remove duplicates
            result["parties"].append({
                "id": org_id,
                "beneficialOwners": [{"id": bo_id} for bo_id in unique_bo_ids]
            })

    return result if result["parties"] else None

def merge_beneficial_owner_identifier(release_json, beneficial_owner_data):
    if not beneficial_owner_data:
        return

    parties = release_json.setdefault("parties", [])

    for new_party in beneficial_owner_data["parties"]:
        existing_party = next((party for party in parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
            new_bo_ids = set(bo["id"] for bo in new_party["beneficialOwners"])
            existing_bo_ids = set(bo["id"] for bo in existing_beneficial_owners)
            
            # Add only new beneficial owners
            for bo_id in new_bo_ids - existing_bo_ids:
                existing_beneficial_owners.append({"id": bo_id})
        else:
            parties.append(new_party)