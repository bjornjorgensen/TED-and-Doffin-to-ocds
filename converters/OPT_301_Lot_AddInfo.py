# converters/OPT_301_Lot_AddInfo.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_additional_info_provider_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    lots = root.xpath("//cac:ProcurementProjectLot", namespaces=namespaces)
    
    for lot in lots:
        additional_info_provider_id = lot.xpath("cac:TenderingTerms/cac:AdditionalInformationParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()", namespaces=namespaces)
        
        if additional_info_provider_id:
            party = {
                "id": additional_info_provider_id[0],
                "roles": ["processContactPoint"]
            }
            result["parties"].append(party)

    return result if result["parties"] else None

def merge_additional_info_provider_identifier(release_json, additional_info_provider_data):
    if not additional_info_provider_data:
        logger.warning("No Additional Info Provider data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in additional_info_provider_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            if "processContactPoint" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("processContactPoint")
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged Additional Info Provider Identifier for {len(additional_info_provider_data['parties'])} parties")
