# converters/opt_301_part_reviewinfo.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_review_info_provider_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse review information provider details from parts.

    Identifies organizations that serve as review information contact points.
    Adds reviewContactPoint role to identified organizations.

    Args:
        xml_content: XML content containing part data

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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:AppealInformationParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    review_info_providers = root.xpath(xpath, namespaces=namespaces)

    if not review_info_providers:
        logger.info("No Review Info Provider Technical Identifier found.")
        return None

    result = {"parties": []}
    for provider in review_info_providers:
        result["parties"].append({"id": provider.text, "roles": ["reviewContactPoint"]})

    return result


def merge_review_info_provider_part(
    release_json: dict[str, Any], review_info_data: dict[str, Any] | None
) -> None:
    """Merge review information provider data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        review_info_data: Review info provider data containing organizations and roles

    Effects:
        Updates the parties section of release_json with reviewContactPoint roles,
        merging with existing party roles where applicable

    """
    if not review_info_data:
        logger.info("No Review Info Provider data to merge.")
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

    logger.info(
        "Merged Review Info Provider data for %d parties.",
        len(review_info_data["parties"]),
    )
