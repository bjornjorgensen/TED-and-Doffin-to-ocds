# converters/OPP_050_Organization.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_buyers_group_lead_indicator(xml_content):
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
        lead_indicator = org.xpath("efbc:GroupLeadIndicator/text()", namespaces=namespaces)
        if lead_indicator and lead_indicator[0].lower() == 'true':
            org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
            if org_id:
                result["parties"].append({
                    "id": org_id[0],
                    "roles": ["leadBuyer"]
                })

    return result if result["parties"] else None

def merge_buyers_group_lead_indicator(release_json, buyers_group_lead_data):
    if not buyers_group_lead_data:
        logger.warning("No Buyers Group Lead Indicator data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in buyers_group_lead_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_roles = existing_party.setdefault("roles", [])
            if "leadBuyer" not in existing_roles:
                existing_roles.append("leadBuyer")
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Buyers Group Lead Indicator for {len(buyers_group_lead_data['parties'])} organizations")