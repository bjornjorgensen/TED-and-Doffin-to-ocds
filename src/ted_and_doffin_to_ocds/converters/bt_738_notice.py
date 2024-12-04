# converters/bt_738_notice.py

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
    """
    Parse BT-738: Preferred publication date for notice.

    Extracts the preferred date for TED publication, converting from the input date format
    to ISO format.

    Args:
        xml_content: XML content to parse, either as string or bytes

    Returns:
        Optional[Dict]: Parsed data in format:
            {
                "tender": {
                    "communication": {
                        "noticePreferredPublicationDate": str  # ISO format date
                    }
                }
            }
        Returns None if no date found or on error
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
    """
    Merge preferred publication date data into the release JSON.

    Updates or adds notice preferred publication date in tender.communication.

    Args:
        release_json: Main OCDS release JSON to update
        pub_date_data: Publication date data to merge, can be None

    Note:
        - Updates release_json in-place
        - Creates tender.communication object if needed
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
