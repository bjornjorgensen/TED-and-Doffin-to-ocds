# converters/BT_500_UBO.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_ubo_name(xml_content):
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
        org_id = organization.xpath("efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        
        if org_id:
            party = {
                "id": org_id[0],
                "beneficialOwners": []
            }
            
            ubos = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces)
            for ubo in ubos:
                ubo_id = ubo.xpath("cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)
                ubo_name = ubo.xpath("cbc:FamilyName/text()", namespaces=namespaces)
                
                if ubo_id and ubo_name:
                    party["beneficialOwners"].append({
                        "id": ubo_id[0],
                        "name": ubo_name[0]
                    })
            
            if party["beneficialOwners"]:
                result["parties"].append(party)

    return result if result["parties"] else None

def merge_ubo_name(release_json, ubo_name_data):
    if not ubo_name_data:
        logger.warning("No UBO Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in ubo_name_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_party.setdefault("beneficialOwners", []).extend(new_party["beneficialOwners"])
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged UBO Name data for {len(ubo_name_data['parties'])} parties")