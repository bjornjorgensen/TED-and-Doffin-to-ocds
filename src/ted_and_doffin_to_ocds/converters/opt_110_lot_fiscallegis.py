import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_fiscal_legislation_url(xml_content: str | bytes) -> dict[str, Any] | None:
    """
    Parse fiscal legislation URL information (OPT-110) from XML content.

    Gets document references from each lot and creates corresponding Document
    objects with URLs and lot references.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing documents with fiscal URLs or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"documents": []}}

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]

                fiscal_docs = lot.xpath(
                    "cac:TenderingTerms/cac:FiscalLegislationDocumentReference",
                    namespaces=NAMESPACES,
                )

                for doc in fiscal_docs:
                    doc_id = doc.xpath("cbc:ID/text()", namespaces=NAMESPACES)
                    url = doc.xpath(
                        "cac:Attachment/cac:ExternalReference/cbc:URI/text()",
                        namespaces=NAMESPACES,
                    )

                    if doc_id and url:
                        result["tender"]["documents"].append(
                            {"id": doc_id[0], "url": url[0], "relatedLots": [lot_id]}
                        )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot data: %s", e)
                continue

        if result["tender"]["documents"]:
            return result

    except Exception:
        logger.exception("Error parsing fiscal legislation URLs")
        return None

    return None


def merge_fiscal_legislation_url(
    release_json: dict[str, Any], fiscal_url_data: dict[str, Any] | None
) -> None:
    """
    Merge fiscal legislation URL information into the release JSON.

    Updates or creates documents with fiscal URLs.
    Preserves existing document data while adding/updating URLs and lot references.

    Args:
        release_json: The target release JSON to update
        fiscal_url_data: The source data containing fiscal URLs to merge

    Returns:
        None
    """
    if not fiscal_url_data:
        logger.warning("No fiscal legislation URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in fiscal_url_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]),
            None,
        )
        if existing_doc:
            existing_doc["url"] = new_doc["url"]
            existing_lots = existing_doc.setdefault("relatedLots", [])
            for lot_id in new_doc["relatedLots"]:
                if lot_id not in existing_lots:
                    existing_lots.append(lot_id)
        else:
            existing_documents.append(new_doc)

    logger.info(
        "Merged fiscal legislation URLs for %d documents",
        len(fiscal_url_data["tender"]["documents"]),
    )
