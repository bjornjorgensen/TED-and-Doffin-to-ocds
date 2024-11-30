# converters/bt_165_organization_company.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_winner_size(xml_content):
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
        company_size = organization.xpath(
            "efac:company/efbc:companySizeCode[@listName='economic-operator-size']/text()",
            namespaces=namespaces,
        )

        if org_id and company_size:
            party = {"id": org_id[0], "details": {"scale": company_size[0]}}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_winner_size(release_json, winner_size_data) -> None:
    if not winner_size_data:
        logger.warning("No Winner Size data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in winner_size_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("details", {}).update(new_party["details"])
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged Winner Size data for %d parties",
        len(winner_size_data["parties"]),
    )
