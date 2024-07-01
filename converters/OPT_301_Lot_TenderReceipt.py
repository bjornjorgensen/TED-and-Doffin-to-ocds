# converters/OPT_301_Lot_TenderReceipt.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_recipient_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:TenderRecipientParty/cac:PartyIdentification/cbc:ID"
    recipient_ids = root.xpath(xpath_query, namespaces=namespaces)

    for recipient_id in recipient_ids:
        party = {
            "id": recipient_id.text,
            "roles": ["submissionReceiptBody"]
        }
        result["parties"].append(party)

    return result if result["parties"] else None

def merge_tender_recipient_identifier(release_json, recipient_data):
    if not recipient_data:
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in recipient_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            if "submissionReceiptBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("submissionReceiptBody")
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged tender recipient data for {len(recipient_data['parties'])} parties")