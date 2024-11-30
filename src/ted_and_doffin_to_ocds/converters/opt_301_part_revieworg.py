# converters/opt_301_part_revieworg.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def part_parse_review_organization(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:AppealReceiverParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    review_organizations = root.xpath(xpath, namespaces=namespaces)

    if not review_organizations:
        logger.info("No Review Organization Technical Identifier found.")
        return None

    result = {"parties": []}
    for organization in review_organizations:
        result["parties"].append({"id": organization.text, "roles": ["reviewBody"]})

    return result


def part_merge_review_organization(release_json, review_organization_data) -> None:
    if not review_organization_data:
        logger.info("No Review Organization data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in review_organization_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "reviewBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewBody")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Review Organization data for %d parties.",
        len(review_organization_data["parties"]),
    )
