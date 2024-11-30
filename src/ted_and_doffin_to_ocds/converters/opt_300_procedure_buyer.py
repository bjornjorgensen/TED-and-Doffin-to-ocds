# converters/opt_300_procedure_buyer.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_buyer_technical_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": [], "buyer": []}

    xpath_query = "/*/cac:ContractingParty/cac:Party/cac:PartyIdentification/cbc:ID"
    buyer_ids = root.xpath(xpath_query, namespaces=namespaces)

    for buyer_id in buyer_ids:
        party = {"id": buyer_id.text, "roles": ["buyer"]}
        result["parties"].append(party)
        result["buyer"].append({"id": buyer_id.text})

    return result if result["parties"] else None


def merge_buyer_technical_identifier(release_json, buyer_data) -> None:
    if not buyer_data:
        return

    parties = release_json.setdefault("parties", [])

    for new_party in buyer_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "buyer" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("buyer")
        else:
            parties.append(new_party)

    # Merge buyers
    existing_buyers = release_json.setdefault("buyer", [])
    new_buyers = buyer_data["buyer"]

    for new_buyer in new_buyers:
        if new_buyer not in existing_buyers:
            existing_buyers.append(new_buyer)

    logger.info("Merged %d buyer(s)", len(buyer_data["parties"]))
