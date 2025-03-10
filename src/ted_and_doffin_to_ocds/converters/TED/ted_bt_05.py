"""BT-05 Notice Dispatch Date converter for TED format.

Maps the notice dispatch date (when the notice was sent for publication)
from TED XML format to OCDS date field in ISO format.
"""

import logging
from datetime import datetime
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

# TED XML namespaces
NAMESPACES = {
    "ted": "http://publications.europa.eu/resource/schema/ted/R2.0.9/publication",
    "n2016": "http://publications.europa.eu/resource/schema/ted/2016/nuts",
    "n2021": "http://publications.europa.eu/resource/schema/ted/2021/nuts",
}

# XPaths for dispatch date in different TED form types
NOTICE_DISPATCH_DATE_XPATHS = [
    "/TED_EXPORT/FORM_SECTION/F01_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F02_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F03_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F04_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F05_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F07_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F08_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F12_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F13_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F15_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/PRIOR_INFORMATION_DEFENCE/FD_PRIOR_INFORMATION_DEFENCE/OTH_INFO_PRIOR_INFORMATION/NOTICE_DISPATCH_DATE",
    "/TED_EXPORT/FORM_SECTION/CONTRACT_CONCESSIONAIRE_DEFENCE/FD_CONTRACT_CONCESSIONAIRE_DEFENCE/COMPLEMENTARY_INFORMATION_CONTRACT_NOTICE_DEFENCE/NOTICE_DISPATCH_DATE",
    "/TED_EXPORT/FORM_SECTION/F21_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F22_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F23_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F24_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
    "/TED_EXPORT/FORM_SECTION/F25_2014/COMPLEMENTARY_INFO/DATE_DISPATCH_NOTICE",
]


def parse_notice_dispatch_date(xml_content: str | bytes) -> str | None:
    """Parse the notice dispatch date (BT-05) from TED XML content.

    Extracts the dispatch date from TED XML and converts it to ISO format.

    Args:
        xml_content: TED XML string or bytes to parse

    Returns:
        ISO formatted datetime string like "2019-11-26T00:00:00+00:00"
        or None if not found

    Raises:
        etree.XMLSyntaxError: If XML content is invalid
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)

        for xpath in NOTICE_DISPATCH_DATE_XPATHS:
            date_nodes = root.xpath(xpath + "/text()")
            if date_nodes:
                date_str = date_nodes[0].strip()
                logger.info("Found notice dispatch date: %s", date_str)
                try:
                    return convert_to_iso_format(date_str)
                except ValueError:
                    logger.exception("Invalid date format: %s", date_str)
        logger.warning("No notice dispatch date found in XML")
        return None  # noqa: TRY300

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise


def _raise_format_error(date_string: str) -> None:
    """Raise a ValueError with a standardized message for invalid date formats.

    Args:
        date_string: The invalid date string

    Raises:
        ValueError: With descriptive message
    """
    msg = f"Unsupported date format: {date_string}"
    raise ValueError(msg)


def convert_to_iso_format(date_string: str) -> str:
    """Convert TED date string to ISO format.

    Converts date string from TED format to ISO format with time set to 00:00:00
    if not specified.

    Args:
        date_string: Date string in format like "YYYY-MM-DD" or with timezone info

    Returns:
        ISO formatted datetime string

    Raises:
        ValueError: If date format is invalid
    """
    try:
        # Handle different date formats from TED
        date_clean = date_string.strip()

        # If the date already has time information
        if "T" in date_clean:
            # Try to parse as ISO format directly
            dt = datetime.fromisoformat(date_clean.replace("Z", "+00:00"))
            return dt.isoformat()

        # If it's just a date (YYYY-MM-DD)
        if len(date_clean.split("-")) == 3:
            # Add default time component
            dt = datetime.fromisoformat(f"{date_clean}T00:00:00+00:00")
            return dt.isoformat()

        # Handle other potential formats
        try:
            # Try to parse with different formats
            for fmt in ("%Y-%m-%d", "%Y%m%d", "%d.%m.%Y"):
                try:
                    dt = datetime.strptime(date_clean, fmt)
                    return dt.replace(tzinfo=datetime.timezone.utc).isoformat()
                except ValueError:
                    continue
        except Exception as e:
            logger.debug("Failed to parse date with standard formats: %s", str(e))

        _raise_format_error(date_string)

    except ValueError as e:
        msg = f"Invalid date format: '{date_string}'"
        raise ValueError(msg) from e


def merge_notice_dispatch_date(
    release_json: dict[str, Any], dispatch_date: str | None
) -> None:
    """Merge notice dispatch date into the release JSON.

    Updates the date field with the ISO formatted dispatch date.

    Args:
        release_json: The target release JSON to update
        dispatch_date: ISO formatted date string to merge
    """
    if dispatch_date:
        release_json["date"] = dispatch_date
        logger.info("Merged notice dispatch date: %s", dispatch_date)
    else:
        logger.debug("No dispatch date to merge")
