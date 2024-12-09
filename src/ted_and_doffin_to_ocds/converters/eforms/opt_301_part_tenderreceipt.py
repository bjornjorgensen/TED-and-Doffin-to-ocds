# converters/opt_301_part_tenderreceipt.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_recipient_part(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse tender recipient references from parts.

    Identifies organizations that receive tender submissions.
    Adds submissionReceiptBody role to identified organizations.

    Args:
        xml_content: XML content containing part data

    Returns:
        Optional[Dict]: Dictionary containing parties with roles, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["submissionReceiptBody"]
                }
            ]
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:TenderRecipientParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    tender_recipients = root.xpath(xpath, namespaces=namespaces)

    if not tender_recipients:
        logger.info("No Tender Recipient Technical Identifier found.")
        return None

    result = {"parties": []}
    for recipient in tender_recipients:
        result["parties"].append(
            {"id": recipient.text, "roles": ["submissionReceiptBody"]}
        )

    return result


def merge_tender_recipient_part(
    release_json: dict[str, Any], tender_recipient_data: dict[str, Any] | None
) -> None:
    """Merge tender recipient data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        tender_recipient_data: Recipient data containing organizations and roles

    Effects:
        Updates the parties section of release_json with submissionReceiptBody roles,
        merging with existing party roles where applicable

    """
    if not tender_recipient_data:
        logger.info("No Tender Recipient data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in tender_recipient_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "submissionReceiptBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("submissionReceiptBody")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Tender Recipient data for %d parties.",
        len(tender_recipient_data["parties"]),
    )
