# converters/OPT_200_Organization_Company.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_organization_technical_identifier(xml_content):
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

    organizations = root.xpath("//efac:Organizations/efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']", namespaces=namespaces)
    
    for org_id in organizations:
        result["parties"].append({
            "id": org_id.text
        })

    return result if result["parties"] else None

def merge_organization_technical_identifier(release_json, org_data):
    if not org_data:
        logger.warning("No Organization Technical Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in org_data["parties"]:
        if not any(party["id"] == new_party["id"] for party in existing_parties):
            existing_parties.append(new_party)

    logger.info(f"Merged Organization Technical Identifier data for {len(org_data['parties'])} organizations")