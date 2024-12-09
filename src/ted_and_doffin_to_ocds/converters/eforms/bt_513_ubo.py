# converters/bt_513_ubo.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_ubo_city(xml_content: str | bytes) -> dict | None:
    """Parse ultimate beneficial owner city information from XML content.

    Args:
        xml_content: XML string or bytes containing UBO data

    Returns:
        Dict containing parsed parties data with city names, or None if no valid data found.
        Format: {
            "parties": [
                {
                    "id": str,
                    "beneficialOwners": [
                        {
                            "id": str,
                            "address": {"locality": str}
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
        if org_id:
            party = {"id": org_id[0], "beneficialOwners": []}

            ubos = root.xpath(
                "//efac:Organizations/efac:UltimateBeneficialOwner",
                namespaces=namespaces,
            )
            for ubo in ubos:
                ubo_id = ubo.xpath(
                    "cbc:ID[@schemeName='ubo']/text()", namespaces=namespaces
                )
                city = ubo.xpath(
                    "cac:ResidenceAddress/cbc:CityName/text()", namespaces=namespaces
                )
                if ubo_id and city:
                    party["beneficialOwners"].append(
                        {"id": ubo_id[0], "address": {"locality": city[0]}}
                    )

            if party["beneficialOwners"]:
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_ubo_city(release_json: dict, ubo_city_data: dict | None) -> None:
    """Merge UBO city data into the release JSON.

    Updates existing parties' beneficial owners information with city names.
    Creates new party entries for organizations not already present in release_json.

    Args:
        release_json: The target release JSON to update
        ubo_city_data: Dictionary containing UBO city data to merge

    Returns:
        None. Updates release_json in place.

    """
    if not ubo_city_data:
        logger.info("No UBO city data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in ubo_city_data["parties"]:
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
                else:
                    existing_beneficial_owners.append(new_ubo)
        else:
            existing_parties.append(new_party)

    logger.info("Merged UBO city data for %d parties", len(ubo_city_data["parties"]))
