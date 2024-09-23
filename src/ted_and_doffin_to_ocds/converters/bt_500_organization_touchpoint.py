# converters/bt_500_organization_touchpoint.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_touchpoint_name(xml_content):
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
        touchpoint_id = organization.xpath(
            "efac:touchpoint/cac:partyIdentification/cbc:ID[@schemeName='touchpoint']/text()",
            namespaces=namespaces,
        )
        touchpoint_name = organization.xpath(
            "efac:touchpoint/cac:partyName/cbc:Name/text()",
            namespaces=namespaces,
        )
        department = organization.xpath(
            "efac:touchpoint/cac:PostalAddress/cbc:Department/text()",
            namespaces=namespaces,
        )
        company_id = organization.xpath(
            "efac:company/cac:partyLegalEntity/cbc:companyID/text()",
            namespaces=namespaces,
        )

        if touchpoint_id and touchpoint_name:
            full_name = touchpoint_name[0]
            if department:
                full_name += f" - {department[0]}"

            party = {"id": touchpoint_id[0], "name": full_name}

            if company_id:
                party["identifier"] = {"id": company_id[0], "scheme": "internal"}

            result["parties"].append(party)

    return result if result["parties"] else None


def merge_touchpoint_name(release_json, touchpoint_name_data):
    if not touchpoint_name_data:
        logger.warning("No touchpoint Name data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in touchpoint_name_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            # Preserve existing name if it already contains department information
            if " - " not in existing_party.get("name", ""):
                existing_party["name"] = new_party["name"]
            if "identifier" not in existing_party and "identifier" in new_party:
                existing_party["identifier"] = new_party["identifier"]
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged touchpoint Name data for {len(touchpoint_name_data['parties'])} parties",
    )
