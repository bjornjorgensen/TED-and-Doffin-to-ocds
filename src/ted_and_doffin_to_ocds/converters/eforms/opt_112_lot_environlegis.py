# converters/opt_112_lot_environlegis.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_environmental_legislation_document_id(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse environmental legislation document ID information (OPT-112) from XML content.

    Gets document IDs from each lot and creates corresponding Document
    objects with type and lot references.

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

        lots = root.xpath(
            "/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
            namespaces=NAMESPACES,
        )

        for lot in lots:
            try:
                lot_id = lot.xpath("cbc:ID/text()", namespaces=NAMESPACES)[0]

                env_docs = lot.xpath(
                    "cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference/cbc:ID/text()",
                    namespaces=NAMESPACES,
                )

                for doc_id in env_docs:
                    if doc_id.strip():
                        result["tender"]["documents"].append(
                            {
                                "id": doc_id,
                                "documentType": "legislation",
                                "relatedLots": [lot_id],
                            }
                        )

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete lot data: %s", e)
                continue

        if result["tender"]["documents"]:
            return result

    except Exception:
        logger.exception("Error parsing environmental legislation document IDs")
        return None

    return None


def merge_environmental_legislation_document_id(
    release_json: dict[str, Any], env_doc_data: dict[str, Any] | None
) -> None:
    """Merge environmental legislation document ID information into the release JSON."""
    if not env_doc_data:
        logger.warning("No environmental legislation document ID data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in env_doc_data["tender"]["documents"]:
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
                existing_doc["documentType"] = "legislation"
                existing_lots = existing_doc.setdefault("relatedLots", [])
                for lot_id in new_doc.get("relatedLots", []):
                    if lot_id not in existing_lots:
                        existing_lots.append(lot_id)
            else:
                existing_documents.append(new_doc)

        except KeyError as e:
            logger.warning("Error accessing document data: %s", e)
            continue

    logger.info(
        "Merged environmental legislation document IDs for %d documents",
        len(env_doc_data["tender"]["documents"]),
    )
