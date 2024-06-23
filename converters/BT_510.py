# converters/BT_510.py
from lxml import etree

def parse_street_address(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }
    
    result = {"parties": []}

    def combine_address_parts(address_element):
        street_name = address_element.xpath("cbc:StreetName/text()", namespaces=namespaces)
        additional_street_name = address_element.xpath("cbc:AdditionalStreetName/text()", namespaces=namespaces)
        address_lines = address_element.xpath("cac:AddressLine/cbc:Line/text()", namespaces=namespaces)
        
        address_parts = street_name + additional_street_name + address_lines
        return ", ".join(filter(None, address_parts)) or None

    # Parse Company Street Address
    company_elements = root.xpath("//efac:Organizations/efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_elements:
        org_id = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        postal_address = company.xpath("cac:PostalAddress", namespaces=namespaces)
        
        if postal_address:
            street_address = combine_address_parts(postal_address[0])
            if street_address:
                party = {
                    "id": org_id,
                    "address": {
                        "streetAddress": street_address
                    }
                }
                result["parties"].append(party)

    # Parse TouchPoint Street Address
    touchpoint_elements = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_elements:
        org_id = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        postal_address = touchpoint.xpath("cac:PostalAddress", namespaces=namespaces)
        company_id = touchpoint.xpath("../efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        if postal_address:
            street_address = combine_address_parts(postal_address[0])
            if street_address:
                party = {
                    "id": org_id,
                    "address": {
                        "streetAddress": street_address
                    }
                }
                if company_id:
                    party["identifier"] = {
                        "id": company_id[0],
                        "scheme": "internal"
                    }
                result["parties"].append(party)

    # Parse UBO Street Address
    ubo_elements = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubo_elements:
        org_id = ubo.xpath("../efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)[0]
        ubo_id = ubo.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        residence_address = ubo.xpath("cac:ResidenceAddress", namespaces=namespaces)
        
        if residence_address:
            street_address = combine_address_parts(residence_address[0])
            if street_address:
                org = next((party for party in result["parties"] if party["id"] == org_id), None)
                if not org:
                    org = {"id": org_id, "beneficialOwners": []}
                    result["parties"].append(org)
                
                beneficial_owner = {
                    "id": ubo_id,
                    "address": {
                        "streetAddress": street_address
                    }
                }
                org.setdefault("beneficialOwners", []).append(beneficial_owner)

    return result if result["parties"] else None

def merge_street_address(release_json, street_address_data):
    if street_address_data and "parties" in street_address_data:
        existing_parties = release_json.setdefault("parties", [])
        
        for new_party in street_address_data["parties"]:
            existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
            if existing_party:
                # Update existing party
                if "address" in new_party and "streetAddress" in new_party["address"]:
                    existing_party.setdefault("address", {})["streetAddress"] = new_party["address"]["streetAddress"]
                if "identifier" in new_party:
                    existing_party["identifier"] = new_party["identifier"]
                if "beneficialOwners" in new_party:
                    existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
                    for new_ubo in new_party["beneficialOwners"]:
                        existing_ubo = next((ubo for ubo in existing_beneficial_owners if ubo["id"] == new_ubo["id"]), None)
                        if existing_ubo:
                            if "address" in new_ubo and "streetAddress" in new_ubo["address"]:
                                existing_ubo.setdefault("address", {})["streetAddress"] = new_ubo["address"]["streetAddress"]
                        else:
                            existing_beneficial_owners.append(new_ubo)
            else:
                # Add new party
                existing_parties.append(new_party)
