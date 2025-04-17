import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# BT-15: Documents URL for Parts
# TED XPaths for defense-related forms:
# - TED_EXPORT/FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/CONTRACTING_AUTHORITY_INFORMATION_DEFENCE/NAME_ADDRESSES_CONTACT_CONTRACT/INTERNET_ADDRESSES_CONTRACT/URL_INFORMATION
# - TED_EXPORT/FORM_SECTION/CONTRACT_CONCESSIONAIRE_DEFENCE/FD_CONTRACT_CONCESSIONAIRE_DEFENCE/CONTRACTING_AUTHORITY_INFORMATION_CONTRACT_SUB_DEFENCE/NAME_ADDRESSES_CONTACT_CONTRACT/INTERNET_ADDRESSES_CONTRACT_DEFENCE/URL_INFORMATION
# OCDS Mapping: tender.documents[].url, documentType


def parse_part_documents_url(
    xml_content: str | bytes,
) -> dict[str, dict[str, list[dict[str, Any]]]] | None:
    """Parses document URLs for parts from TED XML content.

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

        # Handle defense contract forms which have different XPaths
        defense_paths = [
            "FORM_SECTION/CONTRACT_DEFENCE/FD_CONTRACT_DEFENCE/CONTRACTING_AUTHORITY_INFORMATION_DEFENCE/NAME_ADDRESSES_CONTACT_CONTRACT/INTERNET_ADDRESSES_CONTRACT/URL_INFORMATION",
            "FORM_SECTION/CONTRACT_CONCESSIONAIRE_DEFENCE/FD_CONTRACT_CONCESSIONAIRE_DEFENCE/CONTRACTING_AUTHORITY_INFORMATION_CONTRACT_SUB_DEFENCE/NAME_ADDRESSES_CONTACT_CONTRACT/INTERNET_ADDRESSES_CONTRACT_DEFENCE/URL_INFORMATION",
        ]

        document_counter = 1

        for defense_path in defense_paths:
            defense_urls = root.xpath(f"{defense_path}/text()")

            if not defense_urls:
                continue

            for raw_url in defense_urls:
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

                result["tender"]["documents"].append(document)
                logger.info(
                    "Found part document URL %s for document %s from defense contract",
                    clean_url,
                    document_id,
                )

        return result if result["tender"]["documents"] else None

    except Exception:
        logger.exception("Error parsing part document URLs")
        return None


def merge_part_documents_url(
    release_json: dict[str, Any],
    part_documents_url_data: dict[str, dict[str, list[dict[str, Any]]]] | None,
) -> None:
    """Merges the part document URL data into the given release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to merge data into.
        part_documents_url_data (Optional[Dict[str, Dict[str, List[Dict[str, Any]]]]):
            The part document URL data to merge.

    Returns:
        None
    """
    if not part_documents_url_data:
        logger.info("No Part Document URL data to merge")
        return

    existing_documents = release_json.setdefault("tender", {}).setdefault(
        "documents", []
    )

    for new_document in part_documents_url_data["tender"]["documents"]:
        existing_document = next(
            (doc for doc in existing_documents if doc["id"] == new_document["id"]),
            None,
        )

        if existing_document:
            existing_document["url"] = new_document["url"]
            existing_document["documentType"] = new_document["documentType"]
        else:
            existing_documents.append(new_document)

    logger.info(
        "Merged Part Document URL data for %d documents",
        len(part_documents_url_data["tender"]["documents"]),
    )
