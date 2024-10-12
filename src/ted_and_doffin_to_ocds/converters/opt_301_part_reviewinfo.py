# converters/opt_301_part_reviewinfo.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def part_parse_review_info_provider(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:AppealInformationParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    review_info_providers = root.xpath(xpath, namespaces=namespaces)

    if not review_info_providers:
        logger.info("No Review Info Provider Technical Identifier found.")
        return None

    result = {"parties": []}
    for provider in review_info_providers:
        result["parties"].append({"id": provider.text, "roles": ["reviewContactPoint"]})

    return result


def part_merge_review_info_provider(release_json, review_info_provider_data):
    if not review_info_provider_data:
        logger.info("No Review Info Provider data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in review_info_provider_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "reviewContactPoint" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("reviewContactPoint")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Review Info Provider data for %d parties.",
        len(review_info_provider_data["parties"]),
    )
