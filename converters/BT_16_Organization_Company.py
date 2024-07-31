# converters/BT_16_Organization_Company.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_organization_part_name(xml_content):
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
        org_part = org.xpath("efac:Company/cac:PostalAddress/cbc:Department/text()", namespaces=namespaces)
        
        if org_id and org_name:
            full_name = org_name[0]
            if org_part:
                full_name += f" - {org_part[0]}"
            
            organizations.append({
                "id": org_id[0],
                "name": full_name
            })

    logger.info(f"Parsed organization part name data: {organizations}")
    return {"parties": organizations} if organizations else None

def merge_organization_part_name(release_json, organization_part_name_data):
    if not organization_part_name_data:
        logger.warning("No Organization Part Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_org in organization_part_name_data["parties"]:
        existing_org = next((org for org in existing_parties if org["id"] == new_org["id"]), None)
        if existing_org:
            # Preserve existing name if it's already set
            if "name" not in existing_org or not existing_org["name"]:
                existing_org["name"] = new_org["name"]
            elif " - " not in existing_org["name"]:
                # Append department name only if it's not already there
                existing_org["name"] += f" - {new_org['name'].split(' - ', 1)[1]}"
        else:
            existing_parties.append(new_org)

    logger.info(f"Merged Organization Part Name data for {len(organization_part_name_data['parties'])} organizations")
    logger.debug(f"Release JSON after merging Organization Part Name data: {release_json}")