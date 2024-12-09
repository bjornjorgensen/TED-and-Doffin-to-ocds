# converters/opt_301_lot_tendereval.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_tender_evaluator(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse tender evaluation organization references from lots.

    Identifies organizations that serve as evaluation bodies.
    Adds evaluationBody role to identified organizations.

    Note: While eForms allows evaluators to differ per lot, this is rarely used in practice.
    Contact data@open-contracting.org if you have such a use case.

    Args:
        xml_content: XML content containing lot data

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

    result = {"parties": []}

    tender_evaluators = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:TenderEvaluationParty/cac:PartyIdentification/cbc:ID",
        namespaces=namespaces,
    )

    for evaluator in tender_evaluators:
        org_id = evaluator.text
        if org_id:
            result["parties"].append({"id": org_id, "roles": ["evaluationBody"]})

    return result if result["parties"] else None


def merge_tender_evaluator(
    release_json: dict[str, Any], tender_evaluator_data: dict[str, Any] | None
) -> None:
    """Merge tender evaluator data into the release JSON.

    Args:
        release_json: Target release JSON to update
        tender_evaluator_data: Evaluator data containing organizations and roles

    Effects:
        Updates the parties section of release_json with evaluationBody roles,
        merging with existing party roles where applicable

    """
    if not tender_evaluator_data:
        logger.info("No Tender Evaluator Technical Identifier Reference data to merge")
        return

    parties = release_json.setdefault("parties", [])

    for new_party in tender_evaluator_data["parties"]:
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party["roles"])
            existing_party["roles"] = list(existing_roles)
        else:
            parties.append(new_party)

    logger.info(
        "Merged Tender Evaluator Technical Identifier Reference data for %d parties",
        len(tender_evaluator_data["parties"]),
    )
