import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-15: Documents URL for Lots
# TED XPaths:
# - TED_EXPORT/FORM_SECTION/F01_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F02_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F04_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F05_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F07_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F08_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F21_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F22_2014/CONTRACTING_BODY/DOCUMENT_FULL
# - TED_EXPORT/FORM_SECTION/F24_2014/CONTRACTING_BODY/DOCUMENT_FULL
# OCDS Mapping: tender.documents[].url, documentType, relatedLots


def parse_lot_documents_url(
    xml_content: str | bytes,
) -> dict[str, dict[str, list[dict[str, Any]]]] | None:
    """Parses document URLs for lots from TED XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict[str, Dict[str, List[Dict[str, Any]]]]]: A dictionary containing document URLs,
        or None if no documents are found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"documents": []}}

        # List of forms to check
        forms_to_check = [
            "F01_2014",
            "F02_2014",
            "F04_2014",
            "F05_2014",
            "F07_2014",
            "F08_2014",
            "F12_2014",
            "F21_2014",
            "F22_2014",
            "F24_2014",
        ]

        document_counter = 1

        for form_name in forms_to_check:
            # Check for the document URL in this form
            document_urls = root.xpath(
                f"FORM_SECTION/{form_name}/CONTRACTING_BODY/DOCUMENT_FULL/URL_DOCUMENT/text()"
            )

            if not document_urls:
                continue

            for raw_url in document_urls:
                clean_url = raw_url.strip()
                if not clean_url:
                    continue

                document_id = f"DOC-{document_counter:04d}"
                document_counter += 1

                document = {
                    "id": document_id,
                    "documentType": "biddingDocuments",
                    "url": clean_url,
                }

                # Check if there are associated lot references in nearby elements
                lot_refs = root.xpath(
                    f"FORM_SECTION/{form_name}/OBJECT_CONTRACT/LOT_DIVISION/LOT_INFO/LOT_NO/text()"
                )

                if lot_refs:
                    document["relatedLots"] = [
                        lot.strip() for lot in lot_refs if lot.strip()
                    ]

                result["tender"]["documents"].append(document)
                logger.info(
                    "Found lot document URL %s for document %s", clean_url, document_id
                )

        return result if result["tender"]["documents"] else None

    except Exception:
        logger.exception("Error parsing lot document URLs")
        return None


def merge_lot_documents_url(
    release_json: dict[str, Any],
    lot_documents_url_data: dict[str, dict[str, list[dict[str, Any]]]] | None,
) -> None:
    """Merges the lot document URL data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        lot_documents_url_data (Optional[Dict[str, Dict[str, List[Dict[str, Any]]]]):
            The lot document URL data to merge.

    Returns:
        None
    """
    if not lot_documents_url_data:
        logger.info("No Lot Document URL data to merge")
        return

    existing_documents = release_json.setdefault("tender", {}).setdefault(
        "documents", []
    )

    for new_document in lot_documents_url_data["tender"]["documents"]:
        existing_document = next(
            (doc for doc in existing_documents if doc["id"] == new_document["id"]),
            None,
        )

        if existing_document:
            existing_document["url"] = new_document["url"]
            existing_document["documentType"] = new_document["documentType"]

            # Handle relatedLots separately
            if "relatedLots" in new_document:
                if "relatedLots" not in existing_document:
                    existing_document["relatedLots"] = []

                # Add new lot references and ensure uniqueness
                existing_document["relatedLots"] = list(
                    set(existing_document["relatedLots"] + new_document["relatedLots"])
                )
        else:
            existing_documents.append(new_document)

    logger.info(
        "Merged Lot Document URL data for %d documents",
        len(lot_documents_url_data["tender"]["documents"]),
    )
