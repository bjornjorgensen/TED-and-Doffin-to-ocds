# converters/OPT_300_Procedure_Buyer.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_procedure_buyer(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    xpath = "/*/cac:ContractingParty/cac:Party/cac:PartyIdentification/cbc:ID"
    buyer_ids = root.xpath(xpath, namespaces=namespaces)

    if buyer_ids:
        buyer_id = buyer_ids[0].text
        return {
            "parties": [
                {
                    "id": buyer_id,
                    "roles": ["buyer"]
                }
            ],
            "buyer": {
                "id": buyer_id
            }
        }
    return None

def merge_procedure_buyer(release_json, buyer_data):
    if not buyer_data:
        logger.warning("No Procedure Buyer data to merge")
        return

    # Update parties
    existing_parties = {party["id"]: party for party in release_json.get("parties", [])}
    for party in buyer_data["parties"]:
        if party["id"] in existing_parties:
            existing_parties[party["id"]]["roles"] = list(set(existing_parties[party["id"]].get("roles", []) + party["roles"]))
        else:
            release_json.setdefault("parties", []).append(party)

    # Update buyer
    release_json["buyer"] = buyer_data["buyer"]

    logger.info(f"Merged Procedure Buyer data for buyer {buyer_data['buyer']['id']}")