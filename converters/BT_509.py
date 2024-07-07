# converters/BT_509.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_edelivery_gateway(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": []}

    # Parse Company eDelivery Gateway
    company_elements = root.xpath("//efac:Organizations/efac:Organization/efac:Company", namespaces=namespaces)
    for company in company_elements:
        org_id_elements = company.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        if org_id_elements:
            org_id = org_id_elements[0]
            edelivery_gateway = company.xpath("cac:ServiceProviderParty/cbc:ServiceTypeCode[@listName='edelivery-gateway-type']/text()", namespaces=namespaces)
            if edelivery_gateway:
                party = {
                    "id": org_id,
                    "details": {
                        "eDeliveryGateway": edelivery_gateway[0]
                    }
                }
                result["parties"].append(party)

    # Parse TouchPoint eDelivery Gateway
    touchpoint_elements = root.xpath("//efac:Organizations/efac:Organization/efac:TouchPoint", namespaces=namespaces)
    for touchpoint in touchpoint_elements:
        org_id_elements = touchpoint.xpath("cac:PartyIdentification/cbc:ID/text()", namespaces=namespaces)
        if org_id_elements:
            org_id = org_id_elements[0]
            edelivery_gateway = touchpoint.xpath("cac:ServiceProviderParty/cbc:ServiceTypeCode[@listName='edelivery-gateway-type']/text()", namespaces=namespaces)
            if edelivery_gateway:
                party = {
                    "id": org_id,
                    "details": {
                        "eDeliveryGateway": edelivery_gateway[0]
                    }
                }
                result["parties"].append(party)

    return result if result["parties"] else None

def merge_edelivery_gateway(release_json, edelivery_gateway_data):
    if not edelivery_gateway_data:
        logger.warning("No eDelivery Gateway data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in edelivery_gateway_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged eDelivery Gateway data for {len(edelivery_gateway_data['parties'])} parties")