# converters/opt_140_part_procurement_docs.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_procurement_documents_id_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse procurement document IDs from XML content for procurement project parts.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender documents with IDs,
                       or None if no documents are found

    Example structure:
        {
            "tender": {
                "documents": [
                    {
                        "id": "doc_id"
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
    }

    result = {"tender": {"documents": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces
    )

    for part in parts:
        doc_refs = part.xpath(
            "cac:TenderingTerms/cac:CallForTendersDocumentReference/cbc:ID/text()",
            namespaces=namespaces,
        )

        for doc_id in doc_refs:
            result["tender"]["documents"].append({"id": doc_id})

    return result if result["tender"]["documents"] else None


def merge_procurement_documents_id_part(
    release_json: dict[str, Any], proc_docs_data: dict[str, Any] | None
) -> None:
    """Merge procurement document ID information into the release JSON."""
    if not proc_docs_data:
        logger.warning("No procurement documents ID data to merge")
        return

    parties = release_json.setdefault("parties", [])
    existing_docs = release_json.setdefault("tender", {}).setdefault("documents", [])

    for new_doc in proc_docs_data["tender"]["documents"]:
        if "id" not in new_doc:
            logger.warning("Skipping document without id: %s", new_doc)
            continue

        try:
            # Check if document already exists using safe dictionary access
            if not any(
                doc.get("id") == new_doc["id"] for doc in existing_docs if "id" in doc
            ):
                existing_docs.append(new_doc)

            # Handle parties referenced in document
            new_party = proc_docs_data["parties"][0]
            if "id" not in new_party:
                logger.warning("Skipping party without id")
                continue

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
            logger.warning("Error accessing document/party data: %s", e)
            continue

    logger.info(
        "Merged procurement document IDs for %d documents",
        len(proc_docs_data["tender"]["documents"]),
    )
