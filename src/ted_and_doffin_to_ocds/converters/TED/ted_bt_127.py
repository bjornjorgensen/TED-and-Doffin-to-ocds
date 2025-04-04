import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)

# XPath templates for different TED form types
TED_XPATH_TEMPLATES = [
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F01_2014']/*[local-name()='OBJECT_CONTRACT']/*[local-name()='DATE_PUBLICATION_NOTICE']/text()",
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F04_2014']/*[local-name()='OBJECT_CONTRACT']/*[local-name()='DATE_PUBLICATION_NOTICE']/text()",
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F21_2014']/*[local-name()='OBJECT_CONTRACT']/*[local-name()='DATE_PUBLICATION_NOTICE']/text()",
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='F22_2014']/*[local-name()='OBJECT_CONTRACT']/*[local-name()='DATE_PUBLICATION_NOTICE']/text()",
]


def parse_future_notice_date(xml_content: str | bytes) -> str | None:
    """Parse the future notice date (BT-127) from TED format XML content.

    Args:
        xml_content: The XML content containing the planned date

    Returns:
        Optional[str]: ISO formatted date string with timezone, or None if not found
        Format example: "2020-03-15T00:00:00+01:00"
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        # Try all XPath patterns
        for xpath in TED_XPATH_TEMPLATES:
            date_result = root.xpath(xpath)
            if date_result:
                try:
                    # Convert to ISO format using utility function
                    return start_date(date_result[0])
                except ValueError as e:
                    logger.warning("Error parsing planned date: %s", e)
                    continue

        logger.debug("No future notice date found in TED XML")

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None
    except Exception:
        logger.exception("Error processing future notice date")
        return None
    else:
        return None


def merge_future_notice_date(
    release_json: dict, future_notice_date: str | None
) -> None:
    """Merge future notice date into the release JSON.

    Args:
        release_json: The target release JSON to merge data into
        future_notice_date: ISO formatted date string to be merged
    """
    if future_notice_date:
        if "tender" not in release_json:
            release_json["tender"] = {}
        if "communication" not in release_json["tender"]:
            release_json["tender"]["communication"] = {}
        release_json["tender"]["communication"]["futureNoticeDate"] = future_notice_date
        logger.info("Added future notice date: %s", future_notice_date)
