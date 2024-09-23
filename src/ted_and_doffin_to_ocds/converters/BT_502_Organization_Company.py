# converters/BT_502_Organization_Company.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_contact_point(xml_content):
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
        "//efac:Organizations/efac:Organization", namespaces=namespaces,
    )

    for organization in organizations:
        org_id = organization.xpath(
            "efac:Company/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        contact_name = organization.xpath(
            "efac:Company/cac:Contact/cbc:Name/text()", namespaces=namespaces,
        )

        if org_id and contact_name:
            party = {"id": org_id[0], "contactPoint": {"name": contact_name[0]}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_contact_point(release_json, organization_contact_point_data):
    if not organization_contact_point_data:
        logger.warning("No Organization Contact Point data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_contact_point_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("contactPoint", {}).update(
                new_party["contactPoint"],
            )
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged Organization Contact Point data for {len(organization_contact_point_data['parties'])} parties",
    )
