# converters/opt_170_tenderer_leader.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tendering_party_leader(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse tendering party leader information from XML content.

    For each tenderer:
    - Always adds 'tenderer' role
    - Adds 'leadTenderer' role if GroupLeadIndicator is 'true'

    Args:
        xml_content: XML content containing tendering party data

    Returns:
        Optional[Dict]: Dictionary containing parties with roles, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["tenderer", "leadTenderer"]  # leadTenderer only if group lead
                }
            ]
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"parties": []}

    tenderers = root.xpath("//efac:TenderingParty/efac:Tenderer", namespaces=namespaces)

    for tenderer in tenderers:
        org_id = tenderer.xpath(
            "cbc:ID[@schemeName='organization']/text()", namespaces=namespaces
        )
        is_leader = tenderer.xpath(
            "efbc:GroupLeadIndicator/text()", namespaces=namespaces
        )

        if org_id and is_leader:
            roles = ["tenderer"]
            if is_leader[0].lower() == "true":
                roles.append("leadTenderer")

            result["parties"].append({"id": org_id[0], "roles": roles})

    return result if result["parties"] else None


def merge_tendering_party_leader(
    release_json: dict[str, Any], leader_data: dict[str, Any] | None
) -> None:
    """Merge tendering party leader data into the release JSON.

    Args:
        release_json: Target release JSON to update
        leader_data: Leader data containing party roles

    Effects:
        Updates the parties section of release_json with tendering party roles,
        merging roles for existing parties

    """
    if not leader_data:
        logger.info("No tendering party leader data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in leader_data["parties"]:
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
        "Merged tendering party leader data for %d parties", len(leader_data["parties"])
    )
