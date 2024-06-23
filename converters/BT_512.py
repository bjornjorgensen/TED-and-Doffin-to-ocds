# converters/BT_512.py
from lxml import etree

def parse_organization_post_code(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }
    
    result = {"parties": []}

    # Parse Company Post Code
    company_elements = root.xpath("//efac:Organizations/efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_elements:
        org_id = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        postal_zone = company.xpath("cac:PostalAddress/cbc:PostalZone/text()", namespaces=namespaces)
        
        if postal_zone:
            party = {
                "id": org_id,
                "address": {
                    "postalCode": postal_zone[0]
                }
            }
            result["parties"].append(party)

    # Parse TouchPoint Post Code
    touchpoint_elements = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_elements:
        org_id = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        postal_zone = touchpoint.xpath("cac:PostalAddress/cbc:PostalZone/text()", namespaces=namespaces)
        company_id = touchpoint.xpath("../efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        if postal_zone:
            party = {
                "id": org_id,
                "address": {
                    "postalCode": postal_zone[0]
                }
            }
            if company_id:
                party["identifier"] = {
                    "id": company_id[0],
                    "scheme": "internal"
                }
            result["parties"].append(party)

    # Parse UBO Post Code
    ubo_elements = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubo_elements:
        org_id = ubo.xpath("../efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        ubo_id = ubo.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        postal_zone = ubo.xpath("cac:ResidenceAddress/cbc:PostalZone/text()", namespaces=namespaces)
        
        if postal_zone:
            org = next((party for party in result["parties"] if party["id"] == org_id), None)
            if not org:
                org = {"id": org_id, "beneficialOwners": []}
                result["parties"].append(org)
            
            beneficial_owner = {
                "id": ubo_id,
                "address": {
                    "postalCode": postal_zone[0]
                }
            }
            org.setdefault("beneficialOwners", []).append(beneficial_owner)

    return result if result["parties"] else None

def merge_organization_post_code(release_json, post_code_data):
    if post_code_data and "parties" in post_code_data:
        existing_parties = release_json.setdefault("parties", [])
        
        for new_party in post_code_data["parties"]:
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                # Update existing party
                if "address" in new_party:
                    existing_party.setdefault("address", {}).update(new_party["address"])
                if "identifier" in new_party:
                    existing_party["identifier"] = new_party["identifier"]
                if "beneficialOwners" in new_party:
                    existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
                    for new_ubo in new_party["beneficialOwners"]:
                        existing_ubo = next((ubo for ubo in existing_beneficial_owners if ubo["id"] == new_ubo["id"]), None)
                        if existing_ubo:
                            existing_ubo.setdefault("address", {}).update(new_ubo["address"])
                        else:
                            existing_beneficial_owners.append(new_ubo)
            else:
                # Add new party
                existing_parties.append(new_party)
