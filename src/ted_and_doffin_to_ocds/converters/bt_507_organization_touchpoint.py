# converters/bt_507_organization_touchpoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_country_subdivision(xml_content):
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
        company_id = organization.xpath(
            "efac:company/cac:partyLegalEntity/cbc:companyID/text()",
            namespaces=namespaces,
        )
        touchpoint_id = organization.xpath(
            "efac:touchpoint/cac:partyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
            namespaces=namespaces,
        )
        country_subentity_code = organization.xpath(
            "efac:touchpoint/cac:PostalAddress/cbc:CountrySubentityCode[@listName='nuts']/text()",
            namespaces=namespaces,
        )

        if touchpoint_id and country_subentity_code:
            party_data = {
                "id": touchpoint_id[0],
                "address": {"region": country_subentity_code[0]},
            }
            if company_id:
                party_data["identifier"] = {"id": company_id[0], "scheme": "internal"}
            result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_touchpoint_country_subdivision(
    release_json,
    touchpoint_country_subdivision_data,
):
    if not touchpoint_country_subdivision_data:
        logger.warning("No touchpoint country subdivision data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_country_subdivision_data["parties"]:
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
        f"Merged touchpoint country subdivision data for {len(touchpoint_country_subdivision_data['parties'])} parties",
    )
