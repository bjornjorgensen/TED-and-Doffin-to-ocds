# converters/bt_512_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_postcode(xml_content: str | bytes) -> dict | None:
    """
    Parse organization postal code information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization postal code information

    Returns:
        Optional[Dict]: A dictionary containing parsed postal code data in OCDS format with
        'parties' array, or None if no valid postal code data is found.
        Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "address": {
                    "postalCode": "2345"
                }
            }]
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
        postal_zone = organization.xpath(
            "efac:Company/cac:PostalAddress/cbc:PostalZone/text()",
            namespaces=namespaces,
        )

        if org_id and postal_zone:
            party = {"id": org_id[0], "address": {"postalCode": postal_zone[0]}}
            result["parties"].append(party)
            logger.info("Found postal code for organization %s", org_id[0])

    return result if result["parties"] else None


def merge_organization_postcode(
    release_json: dict, organization_postcode_data: dict | None
) -> None:
    """
    Merge organization postal code data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        organization_postcode_data (Optional[Dict]): Organization postal code data to merge,
            containing a 'parties' array with address information

    Returns:
        None: Modifies release_json in place

    Note:
        If organization_postcode_data is None or contains no parties, no changes are made.
        For existing parties, postal code information is updated in the address section.
    """
    if not organization_postcode_data:
        logger.info("No organization postal code data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_postcode_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
            logger.info("Updated postal code for organization %s", new_party["id"])
        else:
            existing_parties.append(new_party)
            logger.info("Added new organization with postal code: %s", new_party["id"])
