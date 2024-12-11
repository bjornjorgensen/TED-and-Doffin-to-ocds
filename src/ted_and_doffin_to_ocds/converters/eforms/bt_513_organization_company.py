# converters/bt_513_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_city(xml_content: str | bytes) -> dict | None:
    """Parse organization city information from XML content.

    Args:
        xml_content: XML string or bytes containing organization data

    Returns:
        Dict containing parsed parties data with city names, or None if no valid data found.
        Format: {
            "parties": [
                {
                    "id": str,
                    "address": {"locality": str}
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
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
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
        city = org.xpath(
            "efac:Company/cac:PostalAddress/cbc:CityName/text()", namespaces=namespaces
        )

        if org_id and city:
            party = {"id": org_id[0], "address": {"locality": city[0]}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_city(
    release_json: dict, organization_city_data: dict | None
) -> None:
    """Merge organization city data into the release JSON.

    Updates existing parties' address information with city names.
    Creates new party entries for organizations not already present in release_json.

    Args:
        release_json: The target release JSON to update
        organization_city_data: Dictionary containing organization city data to merge

    Returns:
        None. Updates release_json in place.

    """
    if not organization_city_data:
        logger.info("No organization city data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_city_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization city data for %d parties",
        len(organization_city_data["parties"]),
    )
