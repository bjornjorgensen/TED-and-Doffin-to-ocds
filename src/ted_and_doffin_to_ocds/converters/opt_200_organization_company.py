# converters/opt_200_organization_company.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_technical_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse organization technical identifiers from XML content.

    Creates basic party entries for organizations found in the XML.
    Only includes organizations that have a technical identifier.

    Args:
        xml_content: XML content containing organization data

    Returns:
        Optional[Dict]: Dictionary containing parties with IDs, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id"
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
        "//efac:Organizations/efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']",
        namespaces=namespaces,
    )

    for org in organizations:
        org_id = org.text
        if org_id:
            result["parties"].append({"id": org_id})

    return result if result["parties"] else None


def merge_organization_technical_identifier(
    release_json: dict[str, Any], org_data: dict[str, Any] | None
) -> None:
    """
    Merge organization technical identifier data into the release JSON.

    Only adds organizations that don't already exist in the parties array.

    Args:
        release_json: Target release JSON to update
        org_data: Organization data containing technical identifiers

    Effects:
        Updates the parties section of release_json with new organizations,
        skipping any that already exist
    """
    if not org_data:
        logger.info("No organization technical identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in org_data["parties"]:
        if not any(
            existing_party["id"] == new_party["id"]
            for existing_party in existing_parties
        ):
            existing_parties.append(new_party)
            logger.info("Added new party with id: %s", new_party["id"])
        else:
            logger.info("Party with id: %s already exists, skipping", new_party["id"])

    logger.info(
        "Merged organization technical identifier data for %d parties",
        len(org_data["parties"]),
    )
