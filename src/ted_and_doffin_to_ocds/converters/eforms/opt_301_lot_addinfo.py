# converters/opt_301_lot_addinfo.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_info_provider(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse additional information provider details from lots.

    Identifies organizations that serve as additional information contact points.
    Adds processContactPoint role to identified organizations.

    Note: While eForms allows different providers per lot, this is rarely used in practice.
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
                    "roles": ["processContactPoint"]
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

    additional_info_parties = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AdditionalInformationParty/cac:PartyIdentification/cbc:ID",
        namespaces=namespaces,
    )

    for party in additional_info_parties:
        org_id = party.text
        if org_id:
            result["parties"].append({"id": org_id, "roles": ["processContactPoint"]})

    return result if result["parties"] else None


def merge_additional_info_provider(
    release_json: dict[str, Any], provider_data: dict[str, Any] | None
) -> None:
    """Merge additional information provider data into the release JSON.

    Args:
        release_json: Target release JSON to update
        provider_data: Provider data containing organizations and roles

    Effects:
        Updates the parties section of release_json with processContactPoint roles,
        merging with existing party roles where applicable

    """
    if not provider_data:
        logger.info(
            "No Additional Info Provider Technical Identifier Reference data to merge"
        )
        return

    parties = release_json.setdefault("parties", [])

    for new_party in provider_data["parties"]:
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
        "Merged Additional Info Provider Technical Identifier Reference data for %s parties",
        len(provider_data["parties"]),
    )
