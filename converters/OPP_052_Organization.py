# converters/OPP_052_Organization.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_acquiring_cpb_buyer_indicator(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
        
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
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
    
    for org in organizations:
        acquiring_cpb_indicator = org.xpath("efbc:AcquiringCPBIndicator/text()", namespaces=namespaces)
        if acquiring_cpb_indicator and acquiring_cpb_indicator[0].lower() == 'true':
            org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
            if org_id:
                result["parties"].append({
                    "id": org_id[0],
                    "roles": ["wholesaleBuyer"]
                })

    return result if result["parties"] else None

def merge_acquiring_cpb_buyer_indicator(release_json, acquiring_cpb_buyer_data):
    if not acquiring_cpb_buyer_data:
        logger.warning("No Acquiring CPB Buyer Indicator data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in acquiring_cpb_buyer_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_roles = existing_party.setdefault("roles", [])
            if "wholesaleBuyer" not in existing_roles:
                existing_roles.append("wholesaleBuyer")
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Acquiring CPB Buyer Indicator for {len(acquiring_cpb_buyer_data['parties'])} organizations")