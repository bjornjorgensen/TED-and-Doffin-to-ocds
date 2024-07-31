# converters/BT_706_UBO.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_ubo_nationality(xml_content):
    """
    Parse the XML content to extract the nationality of Ultimate Beneficial Owners (UBOs).

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed UBO nationality data.
        None: If no relevant data is found.
    """
	
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

    # Find the winning tenderer
    winning_tenderer = root.xpath("//efac:TenderingParty[efac:Tenderer and ../efac:LotTender/cbc:RankCode='1']", namespaces=namespaces)
    
    if winning_tenderer:
        org_id = winning_tenderer[0].xpath("efac:Tenderer/cbc:ID/text()", namespaces=namespaces)[0]
        ubos = root.xpath("//efac:UltimateBeneficialOwner", namespaces=namespaces)
        
        beneficial_owners = []
        for ubo in ubos:
            ubo_id = ubo.xpath("cbc:ID/text()", namespaces=namespaces)[0]
            nationalities = ubo.xpath("efac:Nationality/cbc:NationalityID/text()", namespaces=namespaces)
            
            beneficial_owner = {
                "id": ubo_id,
                "nationalities": [convert_to_iso_3166_1_alpha_2(nat) for nat in nationalities]
            }
            beneficial_owners.append(beneficial_owner)
        
        if beneficial_owners:
            result["parties"].append({
                "id": org_id,
                "beneficialOwners": beneficial_owners
            })

    return result if result["parties"] else None

def convert_to_iso_3166_1_alpha_2(nationality_code):
    """
    Convert nationality code to ISO 3166-1 alpha-2 format.
    This is a placeholder function. In a real implementation, you would use a proper
    conversion table or library to handle all possible codes.
    """
    # Example conversion (incomplete)
    conversion_table = {
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
    return conversion_table.get(nationality_code, nationality_code)

def merge_ubo_nationality(release_json, ubo_nationality_data):
    """
    Merge the parsed UBO nationality data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        ubo_nationality_data (dict): The parsed UBO nationality data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not ubo_nationality_data:
        return

    for new_party in ubo_nationality_data["parties"]:
        existing_party = next((party for party in release_json["parties"] if party["id"] == new_party["id"]), None)
        if existing_party and "roles" in existing_party and "tenderer" in existing_party["roles"]:
            existing_party["beneficialOwners"] = new_party["beneficialOwners"]
            
    logger.info(f"Merged UBO nationality data for {len(ubo_nationality_data['parties'])} parties")