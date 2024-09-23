# converters/BT_503_Organization_TouchPoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_contact_telephone(xml_content):
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
        "//efac:Organizations/efac:Organization",
        namespaces=namespaces,
    )

    for organization in organizations:
        touchpoint_id = organization.xpath(
            "efac:TouchPoint/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
            namespaces=namespaces,
        )
        contact_telephone = organization.xpath(
            "efac:TouchPoint/cac:Contact/cbc:Telephone/text()",
            namespaces=namespaces,
        )
        company_id = organization.xpath(
            "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
            namespaces=namespaces,
        )

        if touchpoint_id and contact_telephone:
            party = {
                "id": touchpoint_id[0],
                "contactPoint": {"telephone": contact_telephone[0]},
            }
            if company_id:
                party["identifier"] = {"id": company_id[0], "scheme": "internal"}
            result["parties"].append(party)

    return result if result["parties"] else None


def merge_touchpoint_contact_telephone(release_json, touchpoint_contact_telephone_data):
    if not touchpoint_contact_telephone_data:
        logger.warning("No TouchPoint Contact Telephone data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_contact_telephone_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("contactPoint", {}).update(
                new_party["contactPoint"],
            )
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged TouchPoint Contact Telephone data for {len(touchpoint_contact_telephone_data['parties'])} parties",
    )
