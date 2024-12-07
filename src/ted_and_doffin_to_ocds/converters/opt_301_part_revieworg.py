# converters/opt_301_part_revieworg.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_organization_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse review organization references from parts.

    Identifies organizations that serve as review bodies.
    Adds reviewBody role to identified organizations.

    Args:
        xml_content: XML content containing part data

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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:AppealReceiverParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    review_organizations = root.xpath(xpath, namespaces=namespaces)

    if not review_organizations:
        logger.info("No Review Organization Technical Identifier found.")
        return None

    result = {"parties": []}
    for organization in review_organizations:
        result["parties"].append({"id": organization.text, "roles": ["reviewBody"]})

    return result


def merge_review_organization_part(
    release_json: dict[str, Any], review_organization_data: dict[str, Any] | None
) -> None:
    """
    Merge review organization data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        review_organization_data: Review organization data containing roles

    Effects:
        Updates the parties section of release_json with reviewBody roles,
        merging with existing party roles where applicable
    """
    if not review_organization_data:
        logger.info("No Review Organization data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in review_organization_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "reviewBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewBody")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Review Organization data for %d parties.",
        len(review_organization_data["parties"]),
    )
