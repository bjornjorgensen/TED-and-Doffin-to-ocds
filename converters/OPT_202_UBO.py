# converters/OPT_202_UBO.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_beneficial_owner_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations/efac:Organization", namespaces=namespaces)
    logger.info(f"Found {len(organizations)} organizations")
    
    for org in organizations:
        org_id = org.xpath(".//efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        logger.info(f"Organization ID: {org_id}")
        if not org_id:
            continue
        org_id = org_id[0]

        ubos = root.xpath("//efac:Organizations/efac:UltimateBeneficialOwner/cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)
        logger.info(f"Found UBOs: {ubos}")
        beneficial_owners = [{"id": ubo_id} for ubo_id in set(ubos)]  # Use set to remove duplicates

        if beneficial_owners:
            result["parties"].append({
                "id": org_id,
                "beneficialOwners": beneficial_owners
            })

    logger.info(f"Parsed beneficial owners: {result}")
    return result if result["parties"] else None

def merge_beneficial_owner_identifier(release_json, ubo_data):
    if not ubo_data:
        logger.warning("No Beneficial Owner Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in ubo_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
            new_bo_ids = set(bo["id"] for bo in new_party["beneficialOwners"])
            existing_bo_ids = set(bo["id"] for bo in existing_beneficial_owners)
            
            for bo_id in new_bo_ids - existing_bo_ids:
                existing_beneficial_owners.append({"id": bo_id})
        else:
            existing_parties.append(new_party)

    #logger.info(f"merge_beneficial_owner_identifier result: {release_json['parties']}")