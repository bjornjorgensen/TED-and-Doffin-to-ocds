# converters/bt_512_organization_touchpoint.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_postcode(xml_content: str | bytes) -> dict | None:
    """Parse organization touchpoint postal code information from XML content.

    Args:
        xml_content: XML string or bytes containing organization touchpoint data

    Returns:
        Dict containing parsed parties data with postal codes, or None if no valid data found.
        Format: {
            "parties": [
                {
                    "id": str,
                    "address": {"postalCode": str},
                    "identifier": {"id": str, "scheme": "internal"} # optional
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
        company_id = organization.xpath(
            "efac:Company/cac:PartyLegalEntity/cbc:companyID/text()",
            namespaces=namespaces,
        )
        touchpoint_id = organization.xpath(
            "efac:TouchPoint/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
            namespaces=namespaces,
        )
        postal_zone = organization.xpath(
            "efac:TouchPoint/cac:PostalAddress/cbc:PostalZone/text()",
            namespaces=namespaces,
        )

        if touchpoint_id and postal_zone:
            party = {"id": touchpoint_id[0], "address": {"postalCode": postal_zone[0]}}
            if company_id:
                party["identifier"] = {"id": company_id[0], "scheme": "internal"}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_touchpoint_postcode(
    release_json: dict, touchpoint_postcode_data: dict | None
) -> None:
    """Merge touchpoint postal code data into the release JSON.

    Updates existing parties' address information with postal codes from touchpoint data.
    Creates new party entries for touchpoints not already present in release_json.

    Args:
        release_json: The target release JSON to update
        touchpoint_postcode_data: Dictionary containing touchpoint postal code data to merge

    Returns:
        None. Updates release_json in place.

    """
    if not touchpoint_postcode_data:
        logger.warning("No touchpoint Postcode data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_postcode_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged touchpoint Postcode data for %s parties",
        len(touchpoint_postcode_data["parties"]),
    )
