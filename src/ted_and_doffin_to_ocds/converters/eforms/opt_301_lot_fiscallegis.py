# converters/opt_301_lot_fiscallegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_fiscal_legislation_org(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse fiscal legislation organization references from lots.

    For each fiscal legislation document:
    - Gets document publisher organization ID
    - Links documents to lots
    - Adds informationService role to publisher organizations

    Args:
        xml_content: XML content containing lot data

    Returns:
        Optional[Dict]: Dictionary containing parties and documents, or None if no data.
        Example structure:
        {
            "parties": [
                {
                    "id": "org_id",
                    "roles": ["informationService"]
                }
            ],
            "tender": {
                "documents": [
                    {
                        "id": "doc_id",
                        "publisher": {"id": "org_id"},
                        "relatedLots": ["lot_id"]
                    }
                ]
            }
        }

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"parties": [], "tender": {"documents": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        fiscal_docs = lot.xpath(
            "cac:TenderingTerms/cac:FiscalLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in fiscal_docs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
            org_id = doc.xpath(
                "cac:IssuerParty/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=namespaces,
            )

            if doc_id and org_id:
                result["tender"]["documents"].append(
                    {
                        "id": doc_id[0],
                        "publisher": {"id": org_id[0]},
                        "relatedLots": [lot_id],
                    }
                )

                if not any(party["id"] == org_id[0] for party in result["parties"]):
                    result["parties"].append(
                        {"id": org_id[0], "roles": ["informationService"]}
                    )

    return result if (result["parties"] or result["tender"]["documents"]) else None


def _merge_party(parties: list, new_party: dict) -> None:
    """Helper to merge a single party."""
    if "id" not in new_party:
        logger.warning("Skipping party without id: %s", new_party)
        return

    try:
        existing_party = next(
            (
                party
                for party in parties
                if "id" in party and party["id"] == new_party["id"]
            ),
            None,
        )
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party.get("roles", []))
            existing_party["roles"] = list(existing_roles)
        else:
            parties.append(new_party)
    except KeyError as e:
        logger.warning("Error accessing party data: %s", e)


def _merge_document(tender_docs: list, new_doc: dict) -> None:
    """Helper to merge a single document."""
    if "id" not in new_doc:
        logger.warning("Skipping document without id: %s", new_doc)
        return

    try:
        existing_doc = next(
            (doc for doc in tender_docs if "id" in doc and doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            if "publisher" in new_doc:
                existing_doc["publisher"] = new_doc["publisher"]
            if "relatedLots" in new_doc:
                existing_lots = set(existing_doc.get("relatedLots", []))
                existing_lots.update(new_doc["relatedLots"])
                existing_doc["relatedLots"] = list(existing_lots)
        else:
            tender_docs.append(new_doc)
    except KeyError as e:
        logger.warning("Error accessing document data: %s", e)


def merge_fiscal_legislation_org(
    release_json: dict[str, Any], fiscal_legis_data: dict[str, Any] | None
) -> None:
    """Merge fiscal legislation organization data into the release JSON."""
    if not fiscal_legis_data:
        logger.info(
            "No Fiscal Legislation Organization Technical Identifier Reference data to merge"
        )
        return

    parties = release_json.setdefault("parties", [])
    tender_docs = release_json.setdefault("tender", {}).setdefault("documents", [])

    for new_party in fiscal_legis_data.get("parties", []):
        _merge_party(parties, new_party)

    for new_doc in fiscal_legis_data.get("tender", {}).get("documents", []):
        _merge_document(tender_docs, new_doc)

    logger.info(
        "Merged Fiscal Legislation Organization Technical Identifier Reference data for %s parties and %s documents",
        len(fiscal_legis_data.get("parties", [])),
        len(fiscal_legis_data.get("tender", {}).get("documents", [])),
    )
