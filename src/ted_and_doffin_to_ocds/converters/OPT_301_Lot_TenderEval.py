# converters/OPT_301_Lot_TenderEval.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_evaluator_identifier(xml_content):
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

    evaluators = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:TenderEvaluationParty/cac:PartyIdentification/cbc:ID",
        namespaces=namespaces,
    )

    for evaluator in evaluators:
        evaluator_id = evaluator.text
        result["parties"].append({"id": evaluator_id, "roles": ["evaluationBody"]})

    return result if result["parties"] else None


def merge_tender_evaluator_identifier(release_json, tender_evaluator_data):
    if not tender_evaluator_data:
        logger.warning("No Tender Evaluator Identifier data to merge")
        return

    existing_parties = release_json.setdefault("parties", [])

    for new_party in tender_evaluator_data["parties"]:
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            if "evaluationBody" not in existing_party.setdefault("roles", []):
                existing_party["roles"].append("evaluationBody")
        else:
            existing_parties.append(new_party)

    logger.info(
        f"Merged Tender Evaluator Identifier data for {len(tender_evaluator_data['parties'])} parties",
    )
