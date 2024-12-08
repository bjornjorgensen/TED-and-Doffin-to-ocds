# converters/bt_513_organization_touchpoint.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_touchpoint_city(
    xml_content: str | bytes,
) -> dict | None:
    """Parse organization touchpoint city information from XML content.

    Args:
        xml_content: XML string or bytes containing organization touchpoint data

    Returns:
        Dict containing parsed parties data with city names, or None if no valid data found.
        Format: {
            "parties": [
                {
                    "id": str,
                    "address": {"locality": str},
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
        touchpoint = org.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            touchpoint = touchpoint[0]
            touchpoint_id = touchpoint.xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            city = touchpoint.xpath(
                "cac:PostalAddress/cbc:CityName/text()", namespaces=namespaces
            )
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and city:
                party = {"id": touchpoint_id[0], "address": {"locality": city[0]}}
                if company_id:
                    party["identifier"] = {"id": company_id[0], "scheme": "internal"}
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_touchpoint_city(
    release_json: dict, organization_touchpoint_city_data: dict | None
) -> None:
    """Merge organization touchpoint city data into the release JSON.

    Updates existing parties' address information with city names from touchpoint data.
    Creates new party entries for touchpoints not already present in release_json.

    Args:
        release_json: The target release JSON to update
        organization_touchpoint_city_data: Dictionary containing touchpoint city data to merge

    Returns:
        None. Updates release_json in place.

    """
    if not organization_touchpoint_city_data:
        logger.info("No organization touchpoint city data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_touchpoint_city_data["parties"]:
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
        "Merged organization touchpoint city data for %d parties",
        len(organization_touchpoint_city_data["parties"]),
    )
