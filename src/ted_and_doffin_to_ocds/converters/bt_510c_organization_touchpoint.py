# converters/bt_510c_organization_touchpoint.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_streetline2(xml_content: str | bytes) -> dict | None:
    """
    Parse touchpoint street line 2 information from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing touchpoint street information

    Returns:
        Optional[Dict]: A dictionary containing parsed address data in OCDS format with
        'parties' array, or None if no valid street data is found.
        Example:
        {
            "parties": [{
                "id": "TPO-0001",
                "address": {
                    "streetAddress": "2, rue de Europe, Building A, 3rd Floor"
                },
                "identifier": {
                    "id": "998298",
                    "scheme": "internal"
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
        touchpoint = organization.xpath("efac:TouchPoint", namespaces=namespaces)
        if touchpoint:
            touchpoint = touchpoint[0]
            touchpoint_id = touchpoint.xpath(
                "cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            company_id = organization.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id:
                street_name = touchpoint.xpath(
                    "cac:PostalAddress/cbc:StreetName/text()",
                    namespaces=namespaces,
                )
                additional_street_name = touchpoint.xpath(
                    "cac:PostalAddress/cbc:AdditionalStreetName/text()",
                    namespaces=namespaces,
                )
                address_lines = touchpoint.xpath(
                    "cac:PostalAddress/cac:AddressLine/cbc:Line/text()",
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
                    party = {
                        "id": touchpoint_id[0],
                        "address": {"streetAddress": street_address},
                    }
                    if company_id:
                        party["identifier"] = {
                            "id": company_id[0],
                            "scheme": "internal",
                        }
                    result["parties"].append(party)
                    logger.info(
                        "Found street line 2 for touchpoint %s", touchpoint_id[0]
                    )

    return result if result["parties"] else None


def merge_touchpoint_streetline2(
    release_json: dict, touchpoint_streetline2_data: dict | None
) -> None:
    """
    Merge touchpoint street line 2 data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        touchpoint_streetline2_data (Optional[Dict]): Touchpoint street data to merge,
            containing a 'parties' array with address and identifier information

    Returns:
        None: Modifies release_json in place

    Note:
        If touchpoint_streetline2_data is None or contains no parties, no changes are made.
        For existing parties, both street address and identifier information is updated.
    """
    if not touchpoint_streetline2_data:
        logger.info("No touchpoint street line 2 data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_streetline2_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
            logger.info("Updated street line 2 for touchpoint %s", new_party["id"])
        else:
            existing_parties.append(new_party)
            logger.info("Added new touchpoint with street line 2: %s", new_party["id"])
