"""BT-05 Notice Dispatch Date/Time converter.

Maps the notice dispatch date and time (when the notice was sent for publication)
from IssueDate and IssueTime elements to OCDS date field in ISO format.
"""

import logging
from datetime import datetime
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_notice_dispatch_date_time(xml_content: str | bytes) -> str | None:
    """Parse the notice dispatch date/time (BT-05) from XML content.

    Combines IssueDate and IssueTime elements into an ISO formatted datetime string.

    Args:
        xml_content: XML string or bytes to parse

    Returns:
        ISO formatted datetime string like "2019-11-26T13:38:54+01:00"
        or None if not found

    Raises:
        etree.XMLSyntaxError: If XML content is invalid

    """
    try:
        if isinstance(xml_content, str):
            xml_content = xml_content.encode("utf-8")

        root = etree.fromstring(xml_content)
        issue_date = root.xpath("/*/cbc:IssueDate/text()", namespaces=NAMESPACES)
        issue_time = root.xpath("/*/cbc:IssueTime/text()", namespaces=NAMESPACES)

        if not (issue_date and issue_time):
            logger.warning("Missing issue date or time in XML")
            return None

        try:
            iso_datetime = convert_to_iso_format(issue_date[0], issue_time[0])
            logger.info("Found notice dispatch datetime: %s", iso_datetime)
            if iso_datetime:
                return iso_datetime
            return None  # noqa: TRY300
        except ValueError:
            logger.exception("Invalid date/time format")
            return None

    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        raise


def convert_to_iso_format(date_string: str, time_string: str) -> str:
    """Convert date and time strings to ISO format.

    Combines separate date (YYYY-MM-DD[+/-]TZ) and time (HH:MM:SS[+/-]TZ) strings into
    a single ISO formatted datetime string. If both date and time have timezone info,
    the timezone from the time string takes precedence.

    Args:
        date_string: Date in YYYY-MM-DD format with optional timezone
        time_string: Time in HH:MM:SS format with optional timezone

    Returns:
        Combined ISO formatted datetime string

    Raises:
        ValueError: If date/time format is invalid
    """

    def _raise_format_error(value: str, field_type: str) -> None:
        msg = f"Invalid {field_type} format: {value}"
        raise ValueError(msg)

    try:
        # Clean date string
        date_clean = date_string.rstrip("Z")  # Remove Z if present
        date_parts = date_clean.split("+")[0].split("-")  # Remove timezone if present
        if len(date_parts) != 3:
            _raise_format_error(date_string, "date")
        clean_date = "-".join(date_parts[:3])  # Keep only YYYY-MM-DD

        # Clean time string and handle timezone
        time_parts = time_string
        if time_parts.endswith("Z"):
            time_parts = time_parts[:-1] + "+00:00"
        elif "+" not in time_parts and "-" not in time_parts:
            time_parts += "+00:00"  # Default to UTC

        # Combine and validate
        datetime_string = f"{clean_date}T{time_parts}"
        date_time = datetime.fromisoformat(datetime_string)
        return date_time.isoformat()

    except (ValueError, IndexError) as e:
        msg = f"Invalid date/time format: date='{date_string}', time='{time_string}'"
        raise ValueError(msg) from e


def merge_notice_dispatch_date_time(
    release_json: dict[str, Any], dispatch_date_time: str | None
) -> None:
    """Merge notice dispatch datetime into the release JSON.

    Updates the date field with the ISO formatted dispatch datetime.

    Args:
        release_json: The target release JSON to update
        dispatch_date_time: ISO formatted datetime string to merge

    """
    if dispatch_date_time:
        release_json["date"] = dispatch_date_time
        logger.info("Merged notice dispatch datetime: %s", dispatch_date_time)
    else:
        logger.debug("No dispatch datetime to merge")
