"""Converter for BT-738-Notice: Preferred publication date for TED notices.

This module handles the extraction and mapping of preferred publication dates for
notices on TED, converting dates to ISO format.
"""

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_notice_preferred_publication_date(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the preferred TED publication date from RequestedPublicationDate.

    Extracts and converts the preferred publication date to ISO format for use in
    tender.communication.noticePreferredPublicationDate.

    Args:
        xml_content: XML content to parse

    Returns:
        dict | None: Parsed data in format:
            {
                "tender": {
                    "communication": {
                        "noticePreferredPublicationDate": str  # ISO format date
                    }
                }
            }
        Returns None if no date found or invalid format

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        requested_date = root.xpath(
            "/*/cbc:RequestedPublicationDate/text()", namespaces=NAMESPACES
        )

        if requested_date:
            try:
                formatted_date = start_date(requested_date[0])
                logger.info("Found preferred publication date: %s", formatted_date)
            except ValueError:
                logger.exception("Invalid date format")
                return None
            else:
                return {
                    "tender": {
                        "communication": {
                            "noticePreferredPublicationDate": formatted_date
                        }
                    }
                }
        else:
            return None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise
    except Exception:
        logger.exception("Error processing preferred publication date")
        return None


def merge_notice_preferred_publication_date(
    release_json: dict, pub_date_data: dict | None
) -> None:
    """Merge preferred publication date into the OCDS release.

    Updates tender.communication.noticePreferredPublicationDate with the
    preferred TED publication date in ISO format.

    Args:
        release_json: Target release JSON to update
        pub_date_data: Publication date data in format:
            {
                "tender": {
                    "communication": {
                        "noticePreferredPublicationDate": str  # ISO format date
                    }
                }
            }

    Note:
        Updates release_json in-place

    """
    if not pub_date_data:
        logger.warning("No notice preferred publication date data to merge")
        return

    tender = release_json.setdefault("tender", {})
    communication = tender.setdefault("communication", {})
    communication["noticePreferredPublicationDate"] = pub_date_data["tender"][
        "communication"
    ]["noticePreferredPublicationDate"]

    logger.info("Merged notice preferred publication date")
