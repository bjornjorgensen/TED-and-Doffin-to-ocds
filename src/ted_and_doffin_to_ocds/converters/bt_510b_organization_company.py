# converters/bt_510b_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_streetline1(xml_content: str | bytes) -> dict | None:
    """Parse organization street address line 1 information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing organization street information

    Returns:
        Optional[Dict]: A dictionary containing parsed address data in OCDS format with
        'parties' array, or None if no valid street data is found.

    Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "address": {
                    "streetAddress": "2, rue de Europe, Building A, 3rd Floor"
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

        if org_id:
            street_name = organization.xpath(
                "efac:Company/cac:PostalAddress/cbc:StreetName/text()",
                namespaces=namespaces,
            )
            additional_street_name = organization.xpath(
                "efac:Company/cac:PostalAddress/cbc:AdditionalStreetName/text()",
                namespaces=namespaces,
            )
            address_lines = organization.xpath(
                "efac:Company/cac:PostalAddress/cac:AddressLine/cbc:Line/text()",
                namespaces=namespaces,
            )

            street_address_parts = []
            if street_name:
                street_address_parts.append(street_name[0])
            if additional_street_name:
                street_address_parts.append(additional_street_name[0])
            street_address_parts.extend(address_lines)

            street_address = ", ".join(street_address_parts)

            if street_address:
                party = {"id": org_id[0], "address": {"streetAddress": street_address}}
                result["parties"].append(party)
                logger.info(
                    "Found street address line 1 for organization %s", org_id[0]
                )

    return result if result["parties"] else None


def merge_organization_streetline1(
    release_json: dict, organization_streetline1_data: dict | None
) -> None:
    """Merge organization street address line 1 data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        organization_streetline1_data (Optional[Dict]): Organization street data to merge,
            containing a 'parties' array with address information

    Returns:
        None: Modifies release_json in place

    Note:
        If organization_streetline1_data is None or contains no parties, no changes are made.
        For existing parties, street address information is updated in the address section.

    """
    if not organization_streetline1_data:
        logger.info("No organization street line 1 data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_streetline1_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
            logger.info(
                "Updated street address line 1 for organization %s", new_party["id"]
            )
        else:
            existing_parties.append(new_party)
            logger.info(
                "Added new organization with street address line 1: %s", new_party["id"]
            )
