# converters/BT_746_Organization.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_winner_listed(xml_content):
    """
    Parse the XML content to extract the winner listed information for each organization.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed winner listed data.
        None: If no relevant data is found.
    """
    # Ensure xml_content is bytes
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

    xpath_query = "//efac:Organization"
    organizations = root.xpath(xpath_query, namespaces=namespaces)
    
    for org in organizations:
        listed_indicator = org.xpath("efbc:ListedOnRegulatedMarketIndicator/text()", namespaces=namespaces)
        org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        
        if listed_indicator and org_id:
            party_data = {
                "id": org_id[0],
                "details": {
                    "listedOnRegulatedMarket": listed_indicator[0].lower() == 'true'
                }
            }
            result["parties"].append(party_data)

    return result if result["parties"] else None

def merge_winner_listed(release_json, winner_listed_data):
    """
    Merge the parsed winner listed data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        winner_listed_data (dict): The parsed winner listed data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not winner_listed_data:
        logger.warning("No winner listed data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in winner_listed_data["parties"]:
        existing_party = next((party for party in parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
        else:
            parties.append(new_party)

    logger.info(f"Merged winner listed data for {len(winner_listed_data['parties'])} organizations")