# converters/BT_512_Organization_TouchPoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_touchpoint_postcode(xml_content):
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
        company_id = organization.xpath("efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()", namespaces=namespaces)
        touchpoint_id = organization.xpath("efac:TouchPoint/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()", namespaces=namespaces)
        postal_zone = organization.xpath("efac:TouchPoint/cac:PostalAddress/cbc:PostalZone/text()", namespaces=namespaces)
        
        if touchpoint_id and postal_zone:
            party = {
                "id": touchpoint_id[0],
                "address": {
                    "postalCode": postal_zone[0]
                }
            }
            if company_id:
                party["identifier"] = {
                    "id": company_id[0],
                    "scheme": "internal"
                }
            result["parties"].append(party)

    return result if result["parties"] else None

def merge_touchpoint_postcode(release_json, touchpoint_postcode_data):
    if not touchpoint_postcode_data:
        logger.warning("No TouchPoint Postcode data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in touchpoint_postcode_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged TouchPoint Postcode data for {len(touchpoint_postcode_data['parties'])} parties")