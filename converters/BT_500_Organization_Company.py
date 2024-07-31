# converters/BT_500_Organization_Company.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_organization_name(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    organizations = []

    org_elements = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    
    for org in org_elements:
        org_id = org.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        org_name = org.xpath("efac:Company/cac:PartyName/cbc:Name/text()", namespaces=namespaces)
        
        if org_id and org_name:
            organizations.append({
                "id": org_id[0],
                "name": org_name[0]
            })

    return {"parties": organizations} if organizations else None

def merge_organization_name(release_json, organization_name_data):
    if not organization_name_data:
        logger.warning("No Organization Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_org in organization_name_data["parties"]:
        existing_org = next((org for org in existing_parties if org["id"] == new_org["id"]), None)
        if existing_org:
            # Preserve existing name if it contains department information
            if " - " not in existing_org.get("name", ""):
                existing_org["name"] = new_org["name"]
        else:
            existing_parties.append(new_org)

    logger.info(f"Merged Organization Name data for {len(organization_name_data['parties'])} parties")