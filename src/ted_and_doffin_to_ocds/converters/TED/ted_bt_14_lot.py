import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_lot_documents_restricted(xml_content: str | bytes) -> dict[str, Any] | None:
    """Parse restricted document references from TED XML content.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing participationFees for restricted documents or None if no data found

    Note:
        According to TED guidance, document restrictions are represented as a
        participation fee of type 'document'
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"tender": {"participationFees": []}}

        # Check the paths for document restricted flags in different form types
        restriction_paths = [
            "//TED_EXPORT/FORM_SECTION/F08_2014/CONTRACTING_BODY/DOCUMENT_RESTRICTED",
            "//TED_EXPORT/FORM_SECTION/F12_2014/CONTRACTING_BODY/DOCUMENT_RESTRICTED",
        ]

        is_restricted = False
        for path in restriction_paths:
            restricted_elements = root.xpath(path)
            if restricted_elements and restricted_elements[0].text:
                text_value = restricted_elements[0].text.strip().upper()
                if text_value in {"YES", "1", "TRUE"}:
                    is_restricted = True
                    break

        if is_restricted:
            # According to TED guidance, add a ParticipationFee object
            result["tender"]["participationFees"].append(
                {
                    "id": "1",
                    "type": "document",
                    "description": "Access to documents is restricted",
                }
            )
            logger.debug("Found document restriction in TED data")

    except Exception:
        logger.exception("Error parsing lot document restrictions")
        return None
    else:
        if is_restricted:
            return result
        return None


def merge_lot_documents_restricted(
    release_json: dict[str, Any], lot_documents_restricted_data: dict[str, Any] | None
) -> None:
    """Merge lot document restrictions into the release JSON.

    Updates or creates participation fees for document restrictions.

    Args:
        release_json: The target release JSON to update
        lot_documents_restricted_data: The source data containing restriction information

    Returns:
        None
    """
    if not lot_documents_restricted_data:
        logger.debug("No document restriction data to merge")
        return

    existing_fees = release_json.setdefault("tender", {}).setdefault(
        "participationFees", []
    )

    for new_fee in lot_documents_restricted_data["tender"]["participationFees"]:
        existing_fee = next(
            (fee for fee in existing_fees if fee["id"] == new_fee["id"]),
            None,
        )

        if existing_fee:
            # Update existing fee
            existing_fee.update(new_fee)
            logger.info("Updated existing participation fee for document restriction")
        else:
            # Add new fee
            existing_fees.append(new_fee)
            logger.info("Added new participation fee for document restriction")
