# converters/BT_500.py
from lxml import etree

def parse_organization_info(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }
    
    result = {"parties": []}

    # Parse Company Names and Identifiers
    company_elements = root.xpath("//efac:Organizations/efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_elements:
        org_id = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        name = company.xpath("cac:PartyName/cbc:Name/text()", namespaces=namespaces)
        company_id = company.xpath("cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        party = {
            "id": org_id
        }
        if name:
            party["name"] = name[0]
        if company_id:
            party["additionalIdentifiers"] = [{
                "id": company_id[0],
                "scheme": "GB-COH"  # Assuming UK Companies House, adjust as needed
            }]
        
        result["parties"].append(party)

    # Parse TouchPoint Names (unchanged)
    touchpoint_elements = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_elements:
        org_id = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        name = touchpoint.xpath("cac:PartyName/cbc:Name/text()", namespaces=namespaces)[0]
        company_id = touchpoint.xpath("../efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        party = {
            "id": org_id,
            "name": name
        }
        if company_id:
            party["identifier"] = {
                "id": company_id[0],
                "scheme": "internal"
            }
        result["parties"].append(party)

    # Parse UBO Names (unchanged)
    ubo_elements = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubo_elements:
        org_id = ubo.xpath("../efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        ubo_id = ubo.xpath("cbc:ID/text()", namespaces=namespaces)
        family_name = ubo.xpath("cbc:FamilyName/text()", namespaces=namespaces)
        
        if org_id and ubo_id and family_name:
            org_id = org_id[0]
            ubo_id = ubo_id[0]
            name = family_name[0]
            
            org = next((party for party in result["parties"] if party["id"] == org_id), None)
            if org:
                org.setdefault("beneficialOwners", []).append({
                    "id": ubo_id,
                    "name": name
                })
            else:
                result["parties"].append({
                    "id": org_id,
                    "beneficialOwners": [{
                        "id": ubo_id,
                        "name": name
                    }]
                })

    return result if result["parties"] else None

def merge_organization_info(release_json, organization_info_data):
    if organization_info_data and "parties" in organization_info_data:
        existing_parties = release_json.setdefault("parties", [])
        
        for new_party in organization_info_data["parties"]:
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                # Update existing party
                if "name" in new_party:
                    existing_party["name"] = new_party["name"]
                if "identifier" in new_party:
                    existing_party["identifier"] = new_party["identifier"]
                if "additionalIdentifiers" in new_party:
                    existing_additional_identifiers = existing_party.setdefault("additionalIdentifiers", [])
                    for new_identifier in new_party["additionalIdentifiers"]:
                        if new_identifier not in existing_additional_identifiers:
                            existing_additional_identifiers.append(new_identifier)
                if "beneficialOwners" in new_party:
                    existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
                    for new_ubo in new_party["beneficialOwners"]:
                        existing_ubo = next((ubo for ubo in existing_beneficial_owners if ubo["id"] == new_ubo["id"]), None)
                        if existing_ubo:
                            existing_ubo.update(new_ubo)
                        else:
                            existing_beneficial_owners.append(new_ubo)
            else:
                # Add new party
                existing_parties.append(new_party)
