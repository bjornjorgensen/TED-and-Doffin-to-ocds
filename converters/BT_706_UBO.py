# converters/BT_706_UBO.py

import logging
from typing import Optional, Dict
from lxml import etree

logger = logging.getLogger(__name__)

code_mapping = {
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

def parse_ubo_nationality(xml_content: str) -> Optional[Dict]:
    """
    Parse the XML content to extract the Ultimate Beneficial Owner's nationality details.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data if found, None otherwise.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
    }

    ubo_nationality = root.xpath("//efext:UBLExtensions/efext:UBLExtension/efext:ExtensionContent/efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
    
    if not ubo_nationality:
        return None

    ubo_data = []
    for ubo in ubo_nationality:
        ubo_id = ubo.xpath("cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)
        nationality = ubo.xpath("efac:Nationality/cbc:NationalityID/text()", namespaces=namespaces)
        
        if ubo_id and nationality:
            two_letter_code = code_mapping.get(nationality[0], nationality[0][:2])
            ubo_data.append({
                "id": ubo_id[0],
                "nationalities": [two_letter_code]
            })

    if ubo_data:
        organization_id = root.xpath("//efac:Organizations/efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        if organization_id:
            return {
                "parties": [
                    {
                        "id": organization_id[0],
                        "beneficialOwners": ubo_data
                    }
                ]
            }

    return None

def merge_ubo_nationality(release_json: Dict, ubo_nationality_data: Optional[Dict]) -> None:
    """
    Merge the parsed UBO nationality data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        ubo_nationality_data (Optional[Dict]): The parsed UBO nationality data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not ubo_nationality_data:
        logger.warning("No UBO nationality data to merge")
        return

    parties = release_json.setdefault("parties", [])
    for party in ubo_nationality_data["parties"]:
        party_id = party["id"]
        existing_party = next((p for p in parties if p["id"] == party_id), None)
        
        if existing_party:
            for new_ubo in party["beneficialOwners"]:
                existing_ubo = next((ubo for ubo in existing_party.get("beneficialOwners", []) if ubo["id"] == new_ubo["id"]), None)
                if existing_ubo:
                    existing_ubo.update(new_ubo)
                else:
                    existing_party.setdefault("beneficialOwners", []).append(new_ubo)
        else:
            parties.append(party)

    logger.info("Merged UBO nationality data")
