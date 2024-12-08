import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_beneficial_owner_reference(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse beneficial owner references from organizations.

    For each organization with beneficial owners:
    - Gets organization ID from Company/PartyIdentification
    - Links beneficial owner IDs to organizations
    - Creates or updates beneficialOwners arrays

    Args:
        xml_content: XML content containing organization data

    Returns:
        Optional[Dict]: Dictionary containing parties with beneficial owners, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "beneficialOwners": [
                        {
                            "id": "ubo_id"
                        }
                    ]
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

    organizations = root.xpath("//efac:Organization", namespaces=namespaces)

    for org in organizations:
        org_id = org.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        ubo_id = org.xpath(
            "efac:UltimateBeneficialOwner/cbc:ID[@schemeName='ubo']/text()",
            namespaces=namespaces,
        )

        if org_id and ubo_id:
            existing_party = next(
                (party for party in result["parties"] if party["id"] == org_id[0]), None
            )

            if existing_party:
                if "beneficialOwners" not in existing_party:
                    existing_party["beneficialOwners"] = []
                if not any(
                    owner["id"] == ubo_id[0]
                    for owner in existing_party["beneficialOwners"]
                ):
                    existing_party["beneficialOwners"].append({"id": ubo_id[0]})
            else:
                result["parties"].append(
                    {"id": org_id[0], "beneficialOwners": [{"id": ubo_id[0]}]}
                )

    return result if result["parties"] else None


def merge_beneficial_owner_reference(
    release_json: dict[str, Any], parsed_data: dict[str, Any] | None
) -> None:
    """Merge beneficial owner reference data into the release JSON.

    Args:
        release_json: Target release JSON to update
        parsed_data: Beneficial owner data containing organizations and owners

    Effects:
        Updates the parties section of release_json with beneficial owner references,
        avoiding duplicate entries

    """
    if not parsed_data:
        return

    parties = release_json.setdefault("parties", [])
    for new_party in parsed_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners", []
            )
            for new_owner in new_party["beneficialOwners"]:
                if not any(
                    owner["id"] == new_owner["id"]
                    for owner in existing_beneficial_owners
                ):
                    existing_beneficial_owners.append(new_owner)
        else:
            parties.append(new_party)

    logger.info("Merged beneficial owner reference data")
