# converters/OPT_301_Lot_TenderEval.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

def parse_tender_evaluator_identifier(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"parties": []}

    xpath_query = "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:TenderEvaluationParty/cac:PartyIdentification/cbc:ID"
    evaluator_ids = root.xpath(xpath_query, namespaces=namespaces)

    for evaluator_id in evaluator_ids:
        party = {
            "id": evaluator_id.text,
            "roles": ["evaluationBody"]
        }
        result["parties"].append(party)

    return result if result["parties"] else None

def merge_tender_evaluator_identifier(release_json, evaluator_data):
    if not evaluator_data:
        return

    existing_parties = release_json.setdefault("parties", [])
    
    for new_party in evaluator_data["parties"]:
        existing_party = next((party for party in existing_parties if party["id"] == new_party["id"]), None)
        if existing_party:
            if "evaluationBody" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("evaluationBody")
        else:
            existing_parties.append(new_party)

    logger.info(f"Merged tender evaluator data for {len(evaluator_data['parties'])} parties")