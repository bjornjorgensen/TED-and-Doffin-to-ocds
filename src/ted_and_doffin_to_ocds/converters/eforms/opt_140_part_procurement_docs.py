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
    """Merge procurement document IDs into the release JSON.

    Args:
        release_json: The target release JSON to merge data into
        proc_docs_data: Procurement document data containing IDs

    Effects:
        Updates the tender.documents section of release_json with new
        procurement document references

    """
    if not proc_docs_data:
        logger.info("No procurement documents ID data for parts to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in proc_docs_data["tender"]["documents"]:
        if not any(doc["id"] == new_doc["id"] for doc in existing_docs):
            existing_docs.append(new_doc)

    logger.info(
        "Merged procurement documents ID data for %d documents (parts)",
        len(proc_docs_data["tender"]["documents"]),
    )
