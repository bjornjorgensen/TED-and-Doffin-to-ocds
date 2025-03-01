# converters/bt_633_organization.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_natural_person(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse the organization natural person indicator (BT-633) from XML content.

    Args:
        xml_content: XML string or bytes containing the procurement data

    Returns:
        Dict containing the parsed natural person data in OCDS format, or None if no data found.
        Format:
        {
            "parties": [
                {
                    "id": "ORG-0001",
                    "details": {
                        "scale": "selfEmployed"
                    }
                }
            ]
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"parties": []}

    organizations = root.xpath(
        "//efac:Organizations/efac:Organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        natural_person_indicator = organization.xpath(
            "efbc:NaturalPersonIndicator/text()",
            namespaces=namespaces,
        )

        if (
            org_id
            and natural_person_indicator
            and natural_person_indicator[0].lower() == "true"
        ):
            party = {"id": org_id[0], "details": {"scale": "selfEmployed"}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_natural_person(
    release_json: dict[str, Any],
    organization_natural_person_data: dict[str, Any] | None,
) -> None:
    """Merge organization natural person data into the release JSON.

    Args:
        release_json: The main release JSON to merge data into
        organization_natural_person_data: The organization natural person data to merge from

    Returns:
        None - modifies release_json in place

    """
    if not organization_natural_person_data:
        logger.warning("No organization Natural Person data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_natural_person_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization Natural Person data for %d parties",
        len(organization_natural_person_data["parties"]),
    )
