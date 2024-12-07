# converters/opt_301_part_tendereval.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_evaluator_part(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse tender evaluator references from parts.

    Identifies organizations that serve as evaluation bodies.
    Adds evaluationBody role to identified organizations.

    Args:
        xml_content: XML content containing part data

    Returns:
        Optional[Dict]: Dictionary containing parties with roles, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["evaluationBody"]
                }
            ]
        }
    """
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


def merge_tender_evaluator_part(
    release_json: dict[str, Any], tender_evaluator_data: dict[str, Any] | None
) -> None:
    """
    Merge tender evaluator data from parts into the release JSON.

    Args:
        release_json: Target release JSON to update
        tender_evaluator_data: Evaluator data containing organizations and roles

    Effects:
        Updates the parties section of release_json with evaluationBody roles,
        merging with existing party roles where applicable
    """
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
