import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_street(xml_content: str | bytes) -> dict | None:
    """Parse UBO (Ultimate Beneficial Owner) street address information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing UBO street information

    Returns:
        Optional[Dict]: A dictionary containing parsed street address data in OCDS format with
        'parties' array, or None if no valid UBO data is found.

    Example:
        {
            "parties": [{
                "id": "ORG-0001",
                "beneficialOwners": [{
                    "id": "UBO-0001",
                    "address": {
                        "streetAddress": "2 CheeseStreet, Nelson Building, 2nd floor"
                    }
                }]
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
            party = {"id": org_id[0], "beneficialOwners": []}

            ubos = root.xpath(
                "//efac:Organizations/efac:UltimateBeneficialOwner",
                namespaces=namespaces,
            )
            for ubo in ubos:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()",
                    namespaces=namespaces,
                )
                street_name = ubo.xpath(
                    "cac:ResidenceAddress/cbc:StreetName/text()",
                    namespaces=namespaces,
                )
                additional_street_name = ubo.xpath(
                    "cac:ResidenceAddress/cbc:AdditionalStreetName/text()",
                    namespaces=namespaces,
                )
                address_lines = ubo.xpath(
                    "cac:ResidenceAddress/cac:AddressLine/cbc:Line/text()",
                    namespaces=namespaces,
                )

                if ubo_id:
                    street_address_parts = []
                    if street_name:
                        street_address_parts.append(street_name[0])
                    if additional_street_name:
                        street_address_parts.append(additional_street_name[0])
                    street_address_parts.extend(address_lines)

                    street_address = ", ".join(street_address_parts)

                    if street_address:
                        beneficial_owner = {
                            "id": ubo_id[0],
                            "address": {"streetAddress": street_address},
                        }
                        party["beneficialOwners"].append(beneficial_owner)
                        logger.info("Found street address for UBO %s", ubo_id[0])

            if party["beneficialOwners"]:
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_ubo_street(release_json: dict, ubo_street_data: dict | None) -> None:
    """Merge UBO street address data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        ubo_street_data (Optional[Dict]): UBO street data to merge,
            containing a 'parties' array with beneficial owner information

    Returns:
        None: Modifies release_json in place

    Note:
        If ubo_street_data is None or contains no parties, no changes are made.
        For existing parties, beneficial owner street address information is updated or added.

    """
    if not ubo_street_data:
        logger.info("No UBO street data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_street_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_beneficial_owners = existing_party.setdefault(
                "beneficialOwners", []
            )
            for new_ubo in new_party["beneficialOwners"]:
                existing_ubo = next(
                    (
                        ubo
                        for ubo in existing_beneficial_owners
                        if ubo["id"] == new_ubo["id"]
                    ),
                    None,
                )
                if existing_ubo:
                    existing_ubo.setdefault("address", {}).update(new_ubo["address"])
                    logger.info("Updated street address for UBO %s", new_ubo["id"])
                else:
                    existing_beneficial_owners.append(new_ubo)
                    logger.info("Added new street address for UBO %s", new_ubo["id"])
        else:
            existing_parties.append(new_party)
            logger.info(
                "Added new party with UBO street addresses: %s", new_party["id"]
            )

    logger.info(
        "Merged UBO street data for %d parties", len(ubo_street_data["parties"])
    )
