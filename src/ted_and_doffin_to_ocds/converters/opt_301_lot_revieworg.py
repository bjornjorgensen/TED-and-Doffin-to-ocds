# converters/opt_301_lot_revieworg.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_organization_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse review organization references from lots.

    Identifies organizations that serve as review bodies.
    Adds reviewBody role to identified organizations.

    Note: While eForms allows review bodies to differ per lot, this is rarely used in practice.
    Contact data@open-contracting.org if you have such a use case.

    Args:
        xml_content: XML content containing lot data

    Returns:
        Optional[Dict]: Dictionary containing parties with roles, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["reviewBody"]
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

    result = {"parties": []}

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AppealTerms/cac:AppealReceiverParty/cac:PartyIdentification/cbc:ID"
    review_org_ids = root.xpath(xpath_query, namespaces=namespaces)

    for review_org_id in review_org_ids:
        party = {"id": review_org_id.text, "roles": ["reviewBody"]}
        result["parties"].append(party)

    return result if result["parties"] else None


def merge_review_organization_identifier(
    release_json: dict[str, Any], review_org_data: dict[str, Any] | None
) -> None:
    """
    Merge review organization data into the release JSON.

    Args:
        release_json: Target release JSON to update
        review_org_data: Review organization data containing roles

    Effects:
        Updates the parties section of release_json with reviewBody roles,
        merging with existing party roles where applicable
    """
    if not review_org_data:
        return

    parties = release_json.setdefault("parties", [])

    for new_party in review_org_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "reviewBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewBody")
        else:
            parties.append(new_party)

    logger.info("Merged %d review organization(s)", len(review_org_data["parties"]))
