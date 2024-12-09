# converters/opt_301_lot_reviewinfo.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_info_provider_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse review information provider details from lots.

    Identifies organizations that serve as review information contact points.
    Adds reviewContactPoint role to identified organizations.

    Note: While eForms allows review info providers to differ per lot, this is rarely used in practice.
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
                    "roles": ["reviewContactPoint"]
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

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AppealTerms/cac:AppealInformationParty/cac:PartyIdentification/cbc:ID"
    review_info_ids = root.xpath(xpath_query, namespaces=namespaces)

    for review_info_id in review_info_ids:
        party = {"id": review_info_id.text, "roles": ["reviewContactPoint"]}
        result["parties"].append(party)

    return result if result["parties"] else None


def merge_review_info_provider_identifier(
    release_json: dict[str, Any], review_info_data: dict[str, Any] | None
) -> None:
    """Merge review information provider data into the release JSON.

    Args:
        release_json: Target release JSON to update
        review_info_data: Review info data containing organizations and roles

    Effects:
        Updates the parties section of release_json with reviewContactPoint roles,
        merging with existing party roles where applicable

    """
    if not review_info_data:
        return

    parties = release_json.setdefault("parties", [])

    for new_party in review_info_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "reviewContactPoint" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewContactPoint")
        else:
            parties.append(new_party)

    logger.info("Merged %d review info provider(s)", len(review_info_data["parties"]))
