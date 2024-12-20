# converters/opt_301_lot_environlegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_environmental_legislation_org(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse environmental legislation organization references from lots.

    For each environmental legislation document:
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
        env_docs = lot.xpath(
            "cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in env_docs:
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


def merge_environmental_legislation_org(
    release_json: dict[str, Any], environ_legis_data: dict[str, Any] | None
) -> None:
    """Merge environmental legislation organization data into the release JSON.

    Args:
        release_json: Target release JSON to update
        environ_legis_data: Environmental legislation data containing organizations and documents

    Effects:
        - Updates parties with informationService roles
        - Updates documents with publisher and lot references
        - Maintains existing data while adding new information

    """
    if not environ_legis_data:
        logger.info(
            "No Environmental Legislation Organization Technical Identifier Reference data to merge"
        )
        return

    parties = release_json.setdefault("parties", [])
    tender_docs = release_json.setdefault("tender", {}).setdefault("documents", [])

    for new_party in environ_legis_data.get("parties", []):
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party["roles"])
            existing_party["roles"] = list(existing_roles)
        else:
            parties.append(new_party)

    for new_doc in environ_legis_data.get("tender", {}).get("documents", []):
        existing_doc = next(
            (doc for doc in tender_docs if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["publisher"] = new_doc["publisher"]
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(set(existing_doc["relatedLots"]))
        else:
            tender_docs.append(new_doc)

    logger.info(
        "Merged Environmental Legislation Organization Technical Identifier Reference data for %s parties and %s documents",
        len(environ_legis_data.get("parties", [])),
        len(environ_legis_data.get("tender", {}).get("documents", [])),
    )
