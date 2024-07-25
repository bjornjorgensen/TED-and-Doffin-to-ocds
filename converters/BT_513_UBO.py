# converters/BT_513_UBO.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

def parse_ubo_city(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
        'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
        'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'
    }

    result = {"parties": []}

    organizations = root.xpath("//efac:Organizations", namespaces=namespaces)
    
    for organization in organizations:
        org_id = organization.xpath("efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()", namespaces=namespaces)
        
        if org_id:
            party = {
                "id": org_id[0],
                "beneficialOwners": []
            }
            
            ubos = organization.xpath("efac:UltimateBeneficialOwner", namespaces=namespaces)
            for ubo in ubos:
                ubo_id = ubo.xpath("cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces)
                city_name = ubo.xpath("cac:ResidenceAddress/cbc:CityName/text()", namespaces=namespaces)
                
                if ubo_id and city_name:
                    beneficial_owner = {
                        "id": ubo_id[0],
                        "address": {
                            "locality": city_name[0]
                        }
                    }
                    party["beneficialOwners"].append(beneficial_owner)
            
            if party["beneficialOwners"]:
                result["parties"].append(party)

    return result if result["parties"] else None

def merge_ubo_city(release_json, ubo_city_data):
    if not ubo_city_data:
        logger.warning("No UBO City data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in ubo_city_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault("beneficialOwners", [])
            for new_bo in new_party["beneficialOwners"]:
                existing_bo = next((bo for bo in existing_beneficial_owners if bo["id"] == new_bo["id"]), None)
                if existing_bo:
                    existing_bo.setdefault("address", {}).update(new_bo["address"])
                else:
                    existing_beneficial_owners.append(new_bo)
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged UBO City data for {len(ubo_city_data['parties'])} parties")