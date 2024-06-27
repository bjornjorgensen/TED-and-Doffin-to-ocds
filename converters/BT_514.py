# converters/BT_514.py
from lxml import etree

# ISO 3166-1 alpha-3 to alpha-2 conversion dictionary for European countries
ISO_3166_CONVERSION = {
    "ALB": "AL",  # Albania
    "AND": "AD",  # Andorra
    "AUT": "AT",  # Austria
    "BLR": "BY",  # Belarus
    "BEL": "BE",  # Belgium
    "BIH": "BA",  # Bosnia and Herzegovina
    "BGR": "BG",  # Bulgaria
    "HRV": "HR",  # Croatia
    "CYP": "CY",  # Cyprus
    "CZE": "CZ",  # Czech Republic
    "DNK": "DK",  # Denmark
    "EST": "EE",  # Estonia
    "FIN": "FI",  # Finland
    "FRA": "FR",  # France
    "DEU": "DE",  # Germany
    "GRC": "GR",  # Greece
    "HUN": "HU",  # Hungary
    "ISL": "IS",  # Iceland
    "IRL": "IE",  # Ireland
    "ITA": "IT",  # Italy
    "KAZ": "KZ",  # Kazakhstan
    "XKX": "XK",  # Kosovo (user-assigned code)
    "LVA": "LV",  # Latvia
    "LIE": "LI",  # Liechtenstein
    "LTU": "LT",  # Lithuania
    "LUX": "LU",  # Luxembourg
    "MLT": "MT",  # Malta
    "MDA": "MD",  # Moldova
    "MCO": "MC",  # Monaco
    "MNE": "ME",  # Montenegro
    "NLD": "NL",  # Netherlands
    "MKD": "MK",  # North Macedonia
    "NOR": "NO",  # Norway
    "POL": "PL",  # Poland
    "PRT": "PT",  # Portugal
    "ROU": "RO",  # Romania
    "RUS": "RU",  # Russia
    "SMR": "SM",  # San Marino
    "SRB": "RS",  # Serbia
    "SVK": "SK",  # Slovakia
    "SVN": "SI",  # Slovenia
    "ESP": "ES",  # Spain
    "SWE": "SE",  # Sweden
    "CHE": "CH",  # Switzerland
    "TUR": "TR",  # Turkey
    "UKR": "UA",  # Ukraine
    "GBR": "GB",  # United Kingdom
    "VAT": "VA",  # Vatican City
}

def convert_country_code(alpha3_code):
    return ISO_3166_CONVERSION.get(alpha3_code, alpha3_code)

def parse_organization_country_code(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }
    
    result = {"parties": []}

    # Parse Company Country Code
    company_elements = root.xpath("//efac:Organizations/efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_elements:
        org_id = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        country_code = company.xpath("cac:PostalAddress/cac:Country/cbc:IdentificationCode/text()", namespaces=namespaces)
        
        if org_id and country_code:
            party = {
                "id": org_id[0],
                "address": {
                    "country": convert_country_code(country_code[0])
                }
            }
            result["parties"].append(party)

    # Parse TouchPoint Country Code
    touchpoint_elements = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_elements:
        org_id = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        country_code = touchpoint.xpath("cac:PostalAddress/cac:Country/cbc:IdentificationCode/text()", namespaces=namespaces)
        company_id = touchpoint.xpath("../efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        if org_id and country_code:
            party = {
                "id": org_id[0],
                "address": {
                    "country": convert_country_code(country_code[0])
                }
            }
            if company_id:
                party["identifier"] = {
                    "id": company_id[0],
                    "scheme": "internal"
                }
            result["parties"].append(party)

    # Parse UBO Country Code
    ubo_elements = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
    for ubo in ubo_elements:
        org_id = ubo.xpath("../efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        ubo_id = ubo.xpath("cbc:ID/text()", namespaces=namespaces)
        country_code = ubo.xpath("cac:ResidenceAddress/cac:Country/cbc:IdentificationCode/text()", namespaces=namespaces)
        
        if org_id and ubo_id and country_code:
            org = next((party for party in result["parties"] if party["id"] == org_id[0]), None)
            if not org:
                org = {"id": org_id[0], "beneficialOwners": []}
                result["parties"].append(org)
            
            beneficial_owner = {
                "id": ubo_id[0],
                "address": {
                    "country": convert_country_code(country_code[0])
                }
            }
            org.setdefault("beneficialOwners", []).append(beneficial_owner)

    return result if result["parties"] else None

def merge_organization_country_code(release_json, country_code_data):
    if country_code_data and "parties" in country_code_data:
        existing_parties = release_json.setdefault("parties", [])
        
        for new_party in country_code_data["parties"]:
            if "id" not in new_party:
                continue  # Skip parties without an ID

            existing_party = next((party for party in existing_parties if party.get("id") == new_party["id"]), None)
            if existing_party:
                # Update existing party
                if "address" in new_party:
                    existing_party.setdefault("address", {}).update(new_party["address"])
                if "identifier" in new_party:
                    existing_party["identifier"] = new_party["identifier"]
                if "beneficialOwners" in new_party:
                    existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
                    for new_ubo in new_party["beneficialOwners"]:
                        if "id" not in new_ubo:
                            continue  # Skip UBOs without an ID
                        existing_ubo = next((ubo for ubo in existing_beneficial_owners if ubo.get("id") == new_ubo["id"]), None)
                        if existing_ubo:
                            existing_ubo.setdefault("address", {}).update(new_ubo["address"])
                        else:
                            existing_beneficial_owners.append(new_ubo)
            else:
                # Add new party
                existing_parties.append(new_party)
