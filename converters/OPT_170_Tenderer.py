# converters/OPT_170_Tenderer.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tendering_party_leader(xml_content):
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

    tendering_parties = root.xpath("//efac:TenderingParty/efac:Tenderer", namespaces=namespaces)
    
    for tenderer in tendering_parties:
        org_id = tenderer.xpath("cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        is_leader = tenderer.xpath("efbc:GroupLeadIndicator/text()", namespaces=namespaces)

        if org_id:
            org_id = org_id[0]
            roles = ["tenderer"]
            
            if is_leader and is_leader[0].lower() == 'true':
                roles.append("leadTenderer")

            result["parties"].append({
                "id": org_id,
                "roles": roles
            })

    return result if result["parties"] else None

def merge_tendering_party_leader(release_json, tenderer_data):
    if not tenderer_data:
        logger.warning("No Tendering Party Leader data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in tenderer_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party["roles"])
            existing_party["roles"] = list(existing_roles)
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Tendering Party Leader data for {len(tenderer_data['parties'])} parties")