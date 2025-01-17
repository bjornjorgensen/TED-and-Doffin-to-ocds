# converters/opt_160_ubo_firstname.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_firstname(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse ultimate beneficial owner (UBO) first names from XML content.

    Extracts UBO information for each organization, linking UBOs to their organizations
    through the organization ID.

    Args:
        xml_content: XML content containing UBO data

    Returns:
        Optional[Dict]: Dictionary containing parties with beneficial owners, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "beneficialOwners": [
                        {
                            "id": "ubo_id",
                            "name": "first_name"
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

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization", namespaces=namespaces
    )

    for org in organizations:
        org_id = org.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        if not org_id:
            continue

        org_id = org_id[0]
        ubos = root.xpath(
            "//efac:Organizations/efac:UltimateBeneficialOwner", namespaces=namespaces
        )

        beneficial_owners = []
        for ubo in ubos:
            ubo_id = ubo.xpath(
                "cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces
            )
            firstname = ubo.xpath("cbc:FirstName/text()", namespaces=namespaces)

            if ubo_id and firstname:
                beneficial_owners.append({"id": ubo_id[0], "name": firstname[0]})

        if beneficial_owners:
            result["parties"].append(
                {"id": org_id, "beneficialOwners": beneficial_owners}
            )

    return result if result["parties"] else None


def merge_ubo_firstname(
    release_json: dict[str, Any], ubo_data: dict[str, Any] | None
) -> None:
    """Merge ultimate beneficial owner (UBO) first name data into the release JSON.

    Args:
        release_json: Target release JSON to update
        ubo_data: UBO data containing first names

    Effects:
        Updates the parties section of release_json with beneficial owner information,
        merging names where UBOs already exist for organizations

    """
    if not ubo_data:
        logger.info("No UBO first name data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in ubo_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners", []
            )
            for new_bo in new_party["beneficialOwners"]:
                existing_bo = next(
                    (
                        bo
                        for bo in existing_beneficial_owners
                        if bo["id"] == new_bo["id"]
                    ),
                    None,
                )
                if existing_bo:
                    existing_bo["name"] = new_bo["name"]
                else:
                    existing_beneficial_owners.append(new_bo)
        else:
            parties.append(new_party)

    logger.info("Merged UBO first name data for %d parties", len(ubo_data["parties"]))
