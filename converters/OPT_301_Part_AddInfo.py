# converters/OPT_301_Part_AddInfo.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_part_addinfo(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AdditionalInformationParty/cac:PartyIdentification/cbc:ID"
    addinfo_party_ids = root.xpath(xpath, namespaces=namespaces)

    result = {"parties": []}

    for party_id in addinfo_party_ids:
        result["parties"].append({
            "id": party_id.text,
            "roles": ["processContactPoint"]
        })

    return result if result["parties"] else None

def merge_part_addinfo(release_json, addinfo_data):
    if not addinfo_data:
        logger.warning("No Part Additional Info data to merge")
        return

    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in addinfo_data["parties"]:
        if party["id"] in existing_parties:
            existing_roles = set(existing_parties[party["id"]].get("roles", []))
            existing_roles.update(party["roles"])
            existing_parties[party["id"]]["roles"] = list(existing_roles)
        else:
            release_json.setdefault("parties", []).append(party)

    logger.info(f"Merged Part Additional Info data for {len(addinfo_data['parties'])} parties")