# converters/bt_512_organization_company.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_postcode(xml_content):
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
        org_id = organization.xpath(
            "efac:company/cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        postal_zone = organization.xpath(
            "efac:company/cac:PostalAddress/cbc:PostalZone/text()",
            namespaces=namespaces,
        )

        if org_id and postal_zone:
            party = {"id": org_id[0], "address": {"postalCode": postal_zone[0]}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_postcode(release_json, organization_postcode_data):
    if not organization_postcode_data:
        logger.warning("No organization Postcode data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_postcode_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("address", {}).update(new_party["address"])
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization Postcode data for %s parties",
        len(organization_postcode_data["parties"]),
    )
