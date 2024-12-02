# converters/bt_15_Lot_part.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_documents_url(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse document URLs from XML content for lots and parts.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[Dict[str, Any]]: Dictionary containing documents data with URLs and lot references,
                                 or None if no valid data is found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result = {"tender": {"documents": []}}

    # Process Lots
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )
    for lot in lots:
        process_document_references(lot, result, namespaces, is_lot=True)

    # Process parts
    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
        namespaces=namespaces,
    )
    for part in parts:
        process_document_references(part, result, namespaces, is_lot=False)

    return result if result["tender"]["documents"] else None


def process_document_references(
    element: etree._Element,
    result: dict[str, Any],
    namespaces: dict[str, str],
    is_lot: bool,
) -> None:
    """Process document references from a lot or part element.

    Args:
        element (etree._Element): The XML element containing document references
        result (Dict[str, Any]): Dictionary to store the processed documents
        namespaces (Dict[str, str]): XML namespaces
        is_lot (bool): Whether processing a lot (True) or part (False)
    """
    element_id = element.xpath("cbc:ID/text()", namespaces=namespaces)[0]
    document_references = element.xpath(
        "cac:TenderingTerms/cac:CallForTendersDocumentReference[cbc:DocumentType='non-restricted-document' and cac:Attachment/cac:ExternalReference/cbc:URI]",
        namespaces=namespaces,
    )

    for doc_ref in document_references:
        doc_id = doc_ref.xpath("cbc:ID/text()", namespaces=namespaces)
        doc_url = doc_ref.xpath(
            "cac:Attachment/cac:ExternalReference/cbc:URI/text()",
            namespaces=namespaces,
        )

        if doc_id and doc_url:
            document = {
                "id": doc_id[0],
                "documentType": "biddingDocuments",
                "url": doc_url[0],
            }
            if is_lot:
                document["relatedLots"] = [element_id]
            result["tender"]["documents"].append(document)


def merge_documents_url(
    release_json: dict[str, Any], documents_url_data: dict[str, Any] | None
) -> None:
    """Merge document URLs data into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        documents_url_data (Optional[Dict[str, Any]]): Document data containing URLs to merge
    """
    if not documents_url_data:
        logger.warning("No documents URL data to merge")
        return

    existing_documents = release_json.setdefault("tender", {}).setdefault(
        "documents",
        [],
    )

    for new_document in documents_url_data["tender"]["documents"]:
        existing_document = next(
            (doc for doc in existing_documents if doc["id"] == new_document["id"]),
            None,
        )
        if existing_document:
            existing_document.update(new_document)
            if "relatedLots" in new_document:
                existing_document.setdefault("relatedLots", []).extend(
                    new_document["relatedLots"],
                )
                existing_document["relatedLots"] = list(
                    set(existing_document["relatedLots"]),
                )  # Remove duplicates
        else:
            existing_documents.append(new_document)

    logger.info(
        "Merged documents URL data for %d documents",
        len(documents_url_data["tender"]["documents"]),
    )
