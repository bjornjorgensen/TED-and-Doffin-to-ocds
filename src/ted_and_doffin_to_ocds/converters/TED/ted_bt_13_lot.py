import logging
from datetime import datetime
from typing import Any

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)

# XPath templates for different TED form types
TED_XPATH_TEMPLATES = [
    # Standard contracts
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='*']/*[local-name()='PROCEDURE_DEFINITION_CONTRACT_NOTICE']/*[local-name()='ADMINISTRATIVE_INFORMATION_CONTRACT_NOTICE']/*[local-name()='CONDITIONS_OBTAINING_SPECIFICATIONS']/*[local-name()='TIME_LIMIT']",
    # Defence contracts
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']/*[local-name()='CONTRACT_DEFENCE']/*[local-name()='FD_CONTRACT_DEFENCE']/*[local-name()='PROCEDURE_DEFINITION_CONTRACT_NOTICE_DEFENCE']/*[local-name()='ADMINISTRATIVE_INFORMATION_CONTRACT_NOTICE_DEFENCE']/*[local-name()='CONDITIONS_OBTAINING_SPECIFICATIONS']/*[local-name()='TIME_LIMIT']",
    # Alternative paths
    "//*[local-name()='TED_EXPORT']/*[local-name()='FORM_SECTION']//*[local-name()='CONDITIONS_OBTAINING_SPECIFICATIONS']/*[local-name()='TIME_LIMIT']",
]


def parse_additional_info_deadline(
    xml_content: str | bytes,
) -> list[dict[str, Any]] | None:
    """Parse the additional information deadline from TED XML content.

    Args:
        xml_content: The XML content to parse, either as string or bytes

    Returns:
        Optional[List[Dict[str, Any]]]: List of dictionaries containing lot data with enquiry period end dates,
                                      or None if no valid data is found
    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")
        root = etree.fromstring(xml_content)

        deadline_text = None

        # Try all XPath patterns
        for xpath in TED_XPATH_TEMPLATES:
            deadline_result = root.xpath(xpath + "/text()")
            if deadline_result:
                deadline_text = deadline_result[0].strip()
                break

        if not deadline_text:
            logger.debug("No additional information deadline found in TED XML")
            return None

        # Extract date and time from the text
        # TED format often combines date and time in a single text field
        iso_datetime = parse_ted_datetime(deadline_text)
        if not iso_datetime:
            return None

        # TED XML doesn't always clearly identify lots, so we create a single default lot
        # Real lot IDs should be obtained from other BT parsers if available

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None
    except Exception:
        logger.exception("Error processing additional information deadline")
        return None
    else:
        # Return the created lot data directly
        return [{"id": "1", "enquiryPeriod": {"endDate": iso_datetime}}]


def parse_ted_datetime(date_string: str) -> str | None:
    """Parse date string from TED format and convert to ISO format.

    Args:
        date_string: The date string from TED XML

    Returns:
        str: ISO formatted date string, or None if parsing fails
    """
    try:
        # TED dates can be in various formats, try to handle common ones
        # Try to extract and standardize
        date_string = date_string.strip()

        # Try different date formats
        formats = [
            "%d.%m.%Y %H:%M",  # 31.12.2020 14:00
            "%d/%m/%Y %H:%M",  # 31/12/2020 14:00
            "%Y-%m-%d %H:%M:%S",  # 2020-12-31 14:00:00
            "%d.%m.%Y",  # 31.12.2020 (no time)
            "%d/%m/%Y",  # 31/12/2020 (no time)
            "%Y-%m-%d",  # 2020-12-31 (no time)
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_string, fmt)
                return dt.isoformat()
            except ValueError:
                continue

        # If standard formats fail, try using the date_utils helper
        return start_date(date_string)

    except Exception as e:
        logger.warning("Failed to parse TED datetime: %s - %s", date_string, e)
        return None


def merge_additional_info_deadline(
    release_json: dict[str, Any], lots_data: list[dict[str, Any]] | None
) -> None:
    """Merge lots data containing additional information deadlines into the release JSON.

    Args:
        release_json: The release JSON to update
        lots_data: List of lot data containing enquiry period end dates
    """
    if lots_data:
        if "tender" not in release_json:
            release_json["tender"] = {}
        if "lots" not in release_json["tender"]:
            release_json["tender"]["lots"] = []

        for lot_data in lots_data:
            existing_lot = next(
                (
                    lot
                    for lot in release_json["tender"]["lots"]
                    if lot["id"] == lot_data["id"]
                ),
                None,
            )
            if existing_lot:
                existing_lot["enquiryPeriod"] = lot_data["enquiryPeriod"]
            else:
                release_json["tender"]["lots"].append(lot_data)

        logger.info("Added additional information deadline to %d lots", len(lots_data))
