# converters/opt_112_part_environlegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_part_environmental_legislation_document_id(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse part environmental legislation document ID information (OPT-112) from XML content.

    Gets document IDs from parts and creates corresponding Document
    objects with document type.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing documents with IDs or None if no data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"documents": []}}

        env_docs = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
            "/cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference/cbc:ID/text()",
            namespaces=NAMESPACES,
        )

        for doc_id in env_docs:
            if doc_id.strip():
                result["tender"]["documents"].append(
                    {"id": doc_id, "documentType": "legislation"}
                )

        if result["tender"]["documents"]:
            return result

    except Exception:
        logger.exception("Error parsing part environmental legislation document IDs")
        return None

    return None


def merge_part_environmental_legislation_document_id(
    release_json: dict[str, Any], env_doc_data: dict[str, Any] | None
) -> None:
    """Merge part environmental legislation document ID information into the release JSON.

    Updates or creates documents with document type.
    Preserves existing document data while adding/updating type.

    Args:
        release_json: The target release JSON to update
        env_doc_data: The source data containing document IDs to merge

    Returns:
        None

    """
    if not env_doc_data:
        logger.warning("No part environmental legislation document ID data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in env_doc_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            existing_doc["documentType"] = "legislation"
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged part environmental legislation document IDs for %d documents",
        len(env_doc_data["tender"]["documents"]),
    )
