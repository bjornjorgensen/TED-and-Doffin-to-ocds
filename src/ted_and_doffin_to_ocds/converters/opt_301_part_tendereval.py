# converters/opt_301_part_tendereval.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def part_parse_tender_evaluator(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    xpath = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:TenderEvaluationParty/cac:PartyIdentification/cbc:ID[@schemeName='touchpoint']"
    tender_evaluators = root.xpath(xpath, namespaces=namespaces)

    if not tender_evaluators:
        logger.info("No Tender Evaluator Technical Identifier found.")
        return None

    result = {"parties": []}
    for evaluator in tender_evaluators:
        result["parties"].append({"id": evaluator.text, "roles": ["evaluationBody"]})

    return result


def part_merge_tender_evaluator(release_json, tender_evaluator_data):
    if not tender_evaluator_data:
        logger.info("No Tender Evaluator data to merge.")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in tender_evaluator_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            if "evaluationBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("evaluationBody")
        else:
            parties.append(new_party)

    logger.info(
        "Merged Tender Evaluator data for %d parties.",
        len(tender_evaluator_data["parties"]),
    )
