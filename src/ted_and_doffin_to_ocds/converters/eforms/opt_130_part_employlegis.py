# converters/opt_130_part_employlegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_employment_legislation_url_part(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse employment legislation URLs from XML content for procurement project parts.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender documents with IDs and URLs,
                       or None if no documents are found

    Example structure:
        {
            "tender": {
                "documents": [
                    {
                        "id": "doc_id",
                        "url": "doc_url"
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
        empl_docs = part.xpath(
            "cac:TenderingTerms/cac:EmploymentLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in empl_docs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
            url = doc.xpath(
                "cac:Attachment/cac:ExternalReference/cbc:URI/text()",
                namespaces=namespaces,
            )

            if doc_id and url:
                result["tender"]["documents"].append({"id": doc_id[0], "url": url[0]})

    return result if result["tender"]["documents"] else None


def merge_employment_legislation_url_part(
    release_json: dict[str, Any], empl_legislation_data: dict[str, Any] | None
) -> None:
    """Merge employment legislation URL data into the release JSON.

    Args:
        release_json: The target release JSON to merge data into
        empl_legislation_data: Employment legislation data containing document URLs

    Effects:
        Updates the tender.documents section of release_json with new or updated
        employment legislation document references

    """
    if not empl_legislation_data:
        logger.info("No employment legislation URL data for parts to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in empl_legislation_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_docs if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["url"] = new_doc["url"]
        else:
            existing_docs.append(new_doc)

    logger.info(
        "Merged employment legislation URL data for %d documents (parts)",
        len(empl_legislation_data["tender"]["documents"]),
    )