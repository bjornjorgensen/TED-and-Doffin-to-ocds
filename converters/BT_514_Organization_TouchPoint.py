# converters/BT_514_Organization_TouchPoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

# ISO 3166-1 alpha-3 to alpha-2 conversion dictionary for European countries
ISO_3166_CONVERSION = {
    "ALB": "AL", "AND": "AD", "AUT": "AT", "BLR": "BY", "BEL": "BE",
    "BIH": "BA", "BGR": "BG", "HRV": "HR", "CYP": "CY", "CZE": "CZ",
    "DNK": "DK", "EST": "EE", "FIN": "FI", "FRA": "FR", "DEU": "DE",
    "GRC": "GR", "HUN": "HU", "ISL": "IS", "IRL": "IE", "ITA": "IT",
    "KAZ": "KZ", "XKX": "XK", "LVA": "LV", "LIE": "LI", "LTU": "LT",
    "LUX": "LU", "MLT": "MT", "MDA": "MD", "MCO": "MC", "MNE": "ME",
    "NLD": "NL", "MKD": "MK", "NOR": "NO", "POL": "PL", "PRT": "PT",
    "ROU": "RO", "RUS": "RU", "SMR": "SM", "SRB": "RS", "SVK": "SK",
    "SVN": "SI", "ESP": "ES", "SWE": "SE", "CHE": "CH", "TUR": "TR",
    "UKR": "UA", "GBR": "GB", "VAT": "VA"
}

def parse_touchpoint_country(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    
    for organization in organizations:
        touchpoint_id = organization.xpath("efac:TouchPoint/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()", namespaces=namespaces)
        country_code = organization.xpath("efac:TouchPoint/cac:PostalAddress/cac:Country/cbc:IdentificationCode/text()", namespaces=namespaces)
        company_id = organization.xpath("efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        
        if touchpoint_id and country_code:
            party = {
                "id": touchpoint_id[0],
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

    return result if result["parties"] else None

def convert_country_code(code):
    """
    Convert ISO 3166-1 alpha-3 country code to alpha-2 code.
    If the code is not found in the conversion dictionary, return the original code.
    """
    return ISO_3166_CONVERSION.get(code, code)

def merge_touchpoint_country(release_json, touchpoint_country_data):
    if not touchpoint_country_data:
        logger.warning("No TouchPoint Country data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in touchpoint_country_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged TouchPoint Country data for {len(touchpoint_country_data['parties'])} parties")