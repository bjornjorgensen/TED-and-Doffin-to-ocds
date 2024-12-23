# converters/opt_120_lot_environlegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_environmental_legislation_url(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse environmental legislation URL information (OPT-120) from XML content.

    Gets document references from each lot and creates corresponding Document
    objects with URLs and lot references.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing documents with URLs or None if no data found

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

                env_docs = lot.xpath(
                    "cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference",
                    namespaces=NAMESPACES,
                )

                for doc in env_docs:
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
        logger.exception("Error parsing environmental legislation URLs")
        return None

    return None


def merge_environmental_legislation_url(
    release_json: dict[str, Any], env_url_data: dict[str, Any] | None
) -> None:
    """Merge environmental legislation URL information into the release JSON."""
    if not env_url_data:
        logger.warning("No environmental legislation URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in env_url_data["tender"]["documents"]:
        if "id" not in new_doc:
            logger.warning("Skipping document without id: %s", new_doc)
            continue

        try:
            existing_doc = next(
                (
                    doc
                    for doc in existing_documents
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
                existing_documents.append(new_doc)

        except KeyError as e:
            logger.warning("Error accessing document data: %s", e)
            continue

    logger.info(
        "Merged environmental legislation URLs for %d documents",
        len(env_url_data["tender"]["documents"]),
    )
