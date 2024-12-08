import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_mediator_part(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse mediator references from procurement project parts.

    Identifies organizations that serve as mediation bodies.
    Adds mediationBody role to identified organizations.

    Args:
        xml_content: XML content containing part data

    Returns:
        Optional[Dict]: Dictionary containing parties with roles, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["mediationBody"]
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

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:MediationParty/cac:PartyIdentification/cbc:ID[@schemeName='organization']"
    mediators = root.xpath(xpath, namespaces=namespaces)

    if not mediators:
        logger.info("No Mediator Technical Identifier found.")
        return None

    result = {"parties": []}
    for mediator in mediators:
        result["parties"].append({"id": mediator.text, "roles": ["mediationBody"]})

    return result


def merge_mediator_part(
    release_json: dict[str, Any], mediator_data: dict[str, Any] | None
) -> None:
    """Merge mediator data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        mediator_data: Mediator data containing organizations and roles

    Effects:
        Updates the parties section of release_json with mediationBody roles,
        merging with existing party roles where applicable

    """
    if not mediator_data:
        logger.info("No Mediator data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in mediator_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "mediationBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("mediationBody")
        else:
            parties.append(new_party)

    logger.info("Merged Mediator data for %d parties.", len(mediator_data["parties"]))
