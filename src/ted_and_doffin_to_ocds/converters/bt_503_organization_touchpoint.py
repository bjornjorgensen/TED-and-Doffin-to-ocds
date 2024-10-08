# converters/bt_503_organization_touchpoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_organization_touchpoint_telephone(xml_content):
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
            telephone = touchpoint.xpath(
                "cac:Contact/cbc:Telephone/text()", namespaces=namespaces
            )
            company_id = org.xpath(
                "efac:Company/cac:PartyLegalEntity/cbc:CompanyID/text()",
                namespaces=namespaces,
            )

            if touchpoint_id and telephone:
                party = {
                    "id": touchpoint_id[0],
                    "contactPoint": {"telephone": telephone[0]},
                }
                if company_id:
                    party["identifier"] = {"id": company_id[0], "scheme": "internal"}
                result["parties"].append(party)

    return result if result["parties"] else None


def merge_organization_touchpoint_telephone(
    release_json, organization_touchpoint_telephone_data
):
    if not organization_touchpoint_telephone_data:
        logger.info("No organization touchpoint telephone data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in organization_touchpoint_telephone_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            existing_party.setdefault("contactPoint", {}).update(
                new_party["contactPoint"]
            )
            if "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(
        "Merged organization touchpoint telephone data for %d parties",
        len(organization_touchpoint_telephone_data["parties"]),
    )
