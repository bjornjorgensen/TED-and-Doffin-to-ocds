# converters/opt_130_lot_employlegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_employment_legislation_url(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse employment legislation URLs from XML content for procurement project lots.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Optional[Dict]: Dictionary containing tender documents with IDs, URLs and related lots,
                       or None if no documents are found

    Example structure:
        {
            "tender": {
                "documents": [
                    {
                        "id": "doc_id",
                        "url": "doc_url",
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
    }

    result = {"tender": {"documents": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        empl_docs = lot.xpath(
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
                result["tender"]["documents"].append(
                    {"id": doc_id[0], "url": url[0], "relatedLots": [lot_id]}
                )

    return result if result["tender"]["documents"] else None


def merge_employment_legislation_url(
    release_json: dict[str, Any], empl_url_data: dict[str, Any] | None
) -> None:
    """Merge employment legislation URL information into the release JSON."""
    if not empl_url_data:
        logger.warning("No employment legislation URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in empl_url_data["tender"]["documents"]:
        if "id" not in new_doc:
            logger.warning("Skipping document without id: %s", new_doc)
            continue

        try:
            existing_doc = next(
                (
                    doc
                    for doc in existing_docs
                    if "id" in doc and doc["id"] == new_doc["id"]
                ),
                None,
            )
            if existing_doc:
                if "url" in new_doc:
                    existing_doc["url"] = new_doc["url"]
                if "relatedLots" in new_doc:
                    existing_lots = existing_doc.setdefault("relatedLots", [])
                    for lot_id in new_doc["relatedLots"]:
                        if lot_id not in existing_lots:
                            existing_lots.append(lot_id)
            else:
                existing_docs.append(new_doc)

        except KeyError as e:
            logger.warning("Error accessing document data: %s", e)
            continue

    logger.info(
        "Merged employment legislation URLs for %d documents",
        len(empl_url_data["tender"]["documents"]),
    )
