# converters/BT_502_503_505_506_507.py
from lxml import etree

def parse_organization_contact_info(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }
    
    result = {"parties": []}

    # Parse Company Contact Info
    company_elements = root.xpath("//efac:Organizations/efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_elements:
        org_id = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        contact_name = company.xpath("cac:Contact/cbc:Name/text()", namespaces=namespaces)
        contact_telephone = company.xpath("cac:Contact/cbc:Telephone/text()", namespaces=namespaces)
        contact_email = company.xpath("cac:Contact/cbc:ElectronicMail/text()", namespaces=namespaces)
        website_uri = company.xpath("cbc:WebsiteURI/text()", namespaces=namespaces)
        country_subdivision = company.xpath("cac:PostalAddress/cbc:CountrySubentityCode/text()", namespaces=namespaces)
        
        party = {"id": org_id}
        if contact_name or contact_telephone or contact_email:
            party["contactPoint"] = {}
            if contact_name:
                party["contactPoint"]["name"] = contact_name[0]
            if contact_telephone:
                party["contactPoint"]["telephone"] = contact_telephone[0]
            if contact_email:
                party["contactPoint"]["email"] = contact_email[0]
        if website_uri:
            party["details"] = {"url": website_uri[0]}
        if country_subdivision:
            party["address"] = {"region": country_subdivision[0]}
        
        if len(party) > 1:  # If there's more than just the ID
            result["parties"].append(party)

    # Parse TouchPoint Contact Info
    touchpoint_elements = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_elements:
        org_id = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        contact_name = touchpoint.xpath("cac:Contact/cbc:Name/text()", namespaces=namespaces)
        contact_telephone = touchpoint.xpath("cac:Contact/cbc:Telephone/text()", namespaces=namespaces)
        contact_email = touchpoint.xpath("cac:Contact/cbc:ElectronicMail/text()", namespaces=namespaces)
        website_uri = touchpoint.xpath("cbc:WebsiteURI/text()", namespaces=namespaces)
        country_subdivision = touchpoint.xpath("cac:PostalAddress/cbc:CountrySubentityCode/text()", namespaces=namespaces)
        company_id = touchpoint.xpath("../efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        party = {"id": org_id, "contactPoint": {}, "details": {}, "address": {}}
        if contact_name:
            party["contactPoint"]["name"] = contact_name[0]
        if contact_telephone:
            party["contactPoint"]["telephone"] = contact_telephone[0]
        if contact_email:
            party["contactPoint"]["email"] = contact_email[0]
        if website_uri:
            party["details"]["url"] = website_uri[0]
        if country_subdivision:
            party["address"]["region"] = country_subdivision[0]
        if company_id:
            party["identifier"] = {
                "id": company_id[0],
                "scheme": "internal"
            }
        
        if party["contactPoint"] or party["details"] or party["address"]:
            result["parties"].append(party)

    # Parse UBO Contact Info
    ubo_elements = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubo_elements:
        org_id = ubo.xpath("../efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        ubo_id = ubo.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        ubo_telephone = ubo.xpath("cac:Contact/cbc:Telephone/text()", namespaces=namespaces)
        ubo_email = ubo.xpath("cac:Contact/cbc:ElectronicMail/text()", namespaces=namespaces)
        ubo_country_subdivision = ubo.xpath("cac:ResidenceAddress/cbc:CountrySubentityCode/text()", namespaces=namespaces)
        
        org = next((party for party in result["parties"] if party["id"] == org_id), None)
        if not org:
            org = {"id": org_id, "beneficialOwners": []}
            result["parties"].append(org)
        
        beneficial_owner = {"id": ubo_id}
        if ubo_telephone:
            beneficial_owner["telephone"] = ubo_telephone[0]
        if ubo_email:
            beneficial_owner["email"] = ubo_email[0]
        if ubo_country_subdivision:
            beneficial_owner["address"] = {"region": ubo_country_subdivision[0]}
        
        org.setdefault("beneficialOwners", []).append(beneficial_owner)

    return result if result["parties"] else None

def merge_organization_contact_info(release_json, contact_info_data):
    if contact_info_data and "parties" in contact_info_data:
        existing_parties = release_json.setdefault("parties", [])
        
        for new_party in contact_info_data["parties"]:
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                # Update existing party
                if "contactPoint" in new_party:
                    existing_party.setdefault("contactPoint", {}).update(new_party["contactPoint"])
                if "details" in new_party:
                    existing_party.setdefault("details", {}).update(new_party["details"])
                if "address" in new_party:
                    existing_party.setdefault("address", {}).update(new_party["address"])
                if "identifier" in new_party:
                    existing_party["identifier"] = new_party["identifier"]
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
