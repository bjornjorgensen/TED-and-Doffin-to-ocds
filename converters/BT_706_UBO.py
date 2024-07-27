# converters/BT_706_UBO.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

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

def parse_ubo_nationalities(xml_content):
    """
    Parse the XML content to extract the nationalities of ultimate beneficial owners.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed UBO nationality data.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes 
    if isinstance(xml_content, str): 
        xml_content = xml_content.encode('utf-8')

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
    
    for organization in organizations:
        org_id = organization.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        if org_id:
            org_id = org_id[0]
            ubos = root.xpath(f"//efac:Organizations/efac:UltimateBeneficialOwner[preceding-sibling::efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization'] = '{org_id}']", namespaces=namespaces)
            
            beneficial_owners = []
            for ubo in ubos:
                ubo_id = ubo.xpath("cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)
                nationalities = ubo.xpath("efac:Nationality/cbc:NationalityID/text()", namespaces=namespaces)
                
                if ubo_id and nationalities:
                    iso_nationalities = [ISO_3166_CONVERSION.get(nat.upper()) for nat in nationalities if ISO_3166_CONVERSION.get(nat.upper())]
                    if iso_nationalities:
                        beneficial_owners.append({
                            "id": ubo_id[0],
                            "nationalities": iso_nationalities
                        })
            
            if beneficial_owners:
                result["parties"].append({
                    "id": org_id,
                    "beneficialOwners": beneficial_owners
                })

    return result if result["parties"] else None

def merge_ubo_nationalities(release_json, ubo_nationalities_data):
    """
    Merge the parsed UBO nationality data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        ubo_nationalities_data (dict): The parsed UBO nationality data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not ubo_nationalities_data:
        logger.warning("No UBO Nationality data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in ubo_nationalities_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
            for new_bo in new_party["beneficialOwners"]:
                existing_bo = next((bo for bo in existing_beneficial_owners if bo["id"] == new_bo["id"]), None)
                if existing_bo:
                    existing_bo.setdefault("nationalities", []).extend(new_bo["nationalities"])
                    existing_bo["nationalities"] = list(set(existing_bo["nationalities"]))  # Remove duplicates
                else:
                    existing_beneficial_owners.append(new_bo)
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged UBO Nationality data for {len(ubo_nationalities_data['parties'])} parties")