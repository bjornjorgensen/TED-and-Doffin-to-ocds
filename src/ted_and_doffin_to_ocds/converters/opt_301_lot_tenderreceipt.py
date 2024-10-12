# converters/opt_301_lot_tenderreceipt.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_tender_recipient(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"parties": []}

    tender_recipients = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:TenderRecipientParty/cac:PartyIdentification/cbc:ID",
        namespaces=namespaces,
    )

    for recipient in tender_recipients:
        org_id = recipient.text
        if org_id:
            result["parties"].append({"id": org_id, "roles": ["submissionReceiptBody"]})

    return result if result["parties"] else None


def merge_tender_recipient(release_json, tender_recipient_data):
    if not tender_recipient_data:
        logger.info("No Tender Recipient Technical Identifier Reference data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in tender_recipient_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party["roles"])
            existing_party["roles"] = list(existing_roles)
        else:
            parties.append(new_party)

    logger.info(
        "Merged Tender Recipient Technical Identifier Reference data for %d parties",
        len(tender_recipient_data["parties"]),
    )
