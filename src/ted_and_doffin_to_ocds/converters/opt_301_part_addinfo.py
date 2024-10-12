# converters/opt_301_part_addinfo.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def part_parse_additional_info_provider(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AdditionalInformationParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    additional_info_providers = root.xpath(xpath, namespaces=namespaces)

    if not additional_info_providers:
        logger.info("No Additional Info Provider Technical Identifier found.")
        return None

    result = {"parties": []}
    for provider in additional_info_providers:
        result["parties"].append(
            {"id": provider.text, "roles": ["processContactPoint"]}
        )

    return result


def part_merge_additional_info_provider(release_json, additional_info_data):
    if not additional_info_data:
        logger.info("No Additional Info Provider data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in additional_info_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "processContactPoint" not in existing_party["roles"]:
                existing_party["roles"].append("processContactPoint")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Additional Info Provider data for %d parties.",
        len(additional_info_data["parties"]),
    )
