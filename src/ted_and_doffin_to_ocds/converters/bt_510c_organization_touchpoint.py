# converters/bt_510c_organization_touchpoint.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_streetline2(xml_content):
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
        "//efac:organizations/efac:organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        touchpoint = organization.xpath("efac:touchpoint", namespaces=namespaces)
        if touchpoint:
            touchpoint_id = touchpoint[0].xpath(
                "cac:partyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
                namespaces=namespaces,
            )
            company_id = organization.xpath(
                "efac:company/cac:partyLegalEntity/cbc:companyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id:
                street_name = touchpoint[0].xpath(
                    "cac:PostalAddress/cbc:StreetName/text()",
                    namespaces=namespaces,
                )
                additional_street_name = touchpoint[0].xpath(
                    "cac:PostalAddress/cbc:AdditionalStreetName/text()",
                    namespaces=namespaces,
                )
                address_lines = touchpoint[0].xpath(
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

    return result if result["parties"] else None


def merge_touchpoint_streetline2(release_json, touchpoint_streetline2_data) -> None:
    if not touchpoint_streetline2_data:
        logger.warning("No touchpoint Streetline 2 data to merge")
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
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged touchpoint Streetline 2 data for %s parties",
        len(touchpoint_streetline2_data["parties"]),
    )
