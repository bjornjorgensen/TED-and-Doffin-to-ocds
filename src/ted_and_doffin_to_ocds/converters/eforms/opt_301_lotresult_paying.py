# converters/opt_301_lotresult_paying.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_payer_party(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse payer party references from lot results.

    Identifies organizations that serve as payers for lots.
    Adds payer role to identified organizations.

    Note: While eForms allows payer parties to differ per lot, this is rarely used in practice.
    Contact data@open-contracting.org if you have such a use case.

    Args:
        xml_content: XML content containing lot result data

    Returns:
        Optional[Dict]: Dictionary containing parties with roles, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["payer"]
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
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"parties": []}

    payer_parties = root.xpath(
        "//efac:NoticeResult/efac:LotResult/cac:PayerParty/cac:PartyIdentification/cbc:ID[@schemeName='organization']",
        namespaces=namespaces,
    )

    for party in payer_parties:
        org_id = party.text
        if org_id:
            result["parties"].append({"id": org_id, "roles": ["payer"]})

    return result if result["parties"] else None


def merge_payer_party(
    release_json: dict[str, Any], payer_party_data: dict[str, Any] | None
) -> None:
    """Merge payer party data into the release JSON.

    Args:
        release_json: Target release JSON to update
        payer_party_data: Payer party data containing organizations and roles

    Effects:
        Updates the parties section of release_json with payer roles,
        merging with existing party roles where applicable

    """
    if not payer_party_data:
        logger.info("No Payer Party (ID reference) data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in payer_party_data["parties"]:
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
        "Merged Payer Party (ID reference) data for %d parties",
        len(payer_party_data["parties"]),
    )
