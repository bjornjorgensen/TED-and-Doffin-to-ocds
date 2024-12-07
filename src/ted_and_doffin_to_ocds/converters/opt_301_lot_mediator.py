# converters/opt_301_lot_mediator.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_mediator_technical_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse mediator information from lots.

    Identifies organizations that serve as mediation bodies.
    Adds mediationBody role to identified organizations.

    Note: While eForms allows mediators to differ per lot, this is rarely used in practice.
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

    result = {"parties": []}

    xpath_query = "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AppealTerms/cac:MediationParty/cac:PartyIdentification/cbc:ID"
    mediator_ids = root.xpath(xpath_query, namespaces=namespaces)

    for mediator_id in mediator_ids:
        party = {"id": mediator_id.text, "roles": ["mediationBody"]}
        result["parties"].append(party)

    return result if result["parties"] else None


def merge_mediator_technical_identifier(
    release_json: dict[str, Any], mediator_data: dict[str, Any] | None
) -> None:
    """
    Merge mediator data into the release JSON.

    Args:
        release_json: Target release JSON to update
        mediator_data: Mediator data containing organizations and roles

    Effects:
        Updates the parties section of release_json with mediationBody roles,
        merging with existing party roles where applicable
    """
    if not mediator_data:
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

    logger.info("Merged %d mediator(s)", len(mediator_data["parties"]))
