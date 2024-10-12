# converters/opt_301_part_mediator.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def part_parse_mediator(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:AppealTerms/cac:MediationParty/cac:PartyIdentification/cbc:ID[@schemeName='organization']"
    mediators = root.xpath(xpath, namespaces=namespaces)

    if not mediators:
        logger.info("No Mediator Technical Identifier found.")
        return None

    result = {"parties": []}
    for mediator in mediators:
        result["parties"].append({"id": mediator.text, "roles": ["mediationBody"]})

    return result


def part_merge_mediator(release_json, mediator_data):
    if not mediator_data:
        logger.info("No Mediator data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in mediator_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "mediationBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("mediationBody")
        else:
            parties.append(new_party)

    logger.info("Merged Mediator data for %d parties.", len(mediator_data["parties"]))
