import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_part_employment_legislation_document_id(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse part employment legislation document ID information (OPT-113) from XML content.

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

        empl_docs = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']"
            "/cac:TenderingTerms/cac:EmploymentLegislationDocumentReference/cbc:ID/text()",
            namespaces=NAMESPACES,
        )

        for doc_id in empl_docs:
            if doc_id.strip():
                result["tender"]["documents"].append(
                    {"id": doc_id, "documentType": "legislation"}
                )

        if result["tender"]["documents"]:
            return result

    except Exception:
        logger.exception("Error parsing part employment legislation document IDs")
        return None

    return None


def merge_part_employment_legislation_document_id(
    release_json: dict[str, Any], empl_doc_data: dict[str, Any] | None
) -> None:
    """
    Merge part employment legislation document ID information into the release JSON.

    Updates or creates documents with document type.
    Preserves existing document data while adding/updating type.

    Args:
        release_json: The target release JSON to update
        empl_doc_data: The source data containing document IDs to merge

    Returns:
        None
    """
    if not empl_doc_data:
        logger.warning("No part employment legislation document ID data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in empl_doc_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            existing_doc["documentType"] = "legislation"
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged part employment legislation document IDs for %d documents",
        len(empl_doc_data["tender"]["documents"]),
    )
