# converters/BT_746_Organization.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_organization_listed(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }
    
    result = {"parties": []}
    
    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    logger.debug(f"Found {len(organizations)} organizations")
    
    for organization in organizations:
        org_id = organization.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        listed_indicator = organization.xpath("efbc:ListedOnRegulatedMarketIndicator/text()", namespaces=namespaces)
        
        logger.debug(f"Organization ID: {org_id}, Listed Indicator: {listed_indicator}")
        
        if org_id and listed_indicator:
            party = {
                "id": org_id[0],
                "details": {
                    "listedOnRegulatedMarket": listed_indicator[0].lower() == 'true'
                }
            }
            result["parties"].append(party)
            logger.debug(f"Added party: {party}")
    
    logger.debug(f"Parsed result: {result}")
    return result if result["parties"] else None

def merge_organization_listed(release_json, organization_listed_data):
    if not organization_listed_data:
        logger.debug("No organization listed data to merge")
        return
    
    logger.debug(f"Merging organization listed data: {organization_listed_data}")
    
    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in organization_listed_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party["details"] = existing_party.get("details", {})
            existing_party["details"].update(new_party["details"])
            logger.debug(f"Updated existing party: {existing_party}")
        else:
            existing_parties.append(new_party)
            logger.debug(f"Added new party: {new_party}")
    
    logger.debug(f"Merged result: {release_json['parties']}")
