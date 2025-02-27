# converters/bt_13_part.py

import logging
from datetime import datetime
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_info_deadline_part(xml_content: str | bytes) -> str | None:
    """Parse the additional information deadline from XML content for the part.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse, either as string or bytes

    Returns:
        Optional[str]: ISO formatted datetime string for the enquiry period end date, or None if not found

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

    part_element = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']",
        namespaces=namespaces,
    )

    if part_element:
        end_date = part_element[0].xpath(
            "cac:TenderingProcess/cac:AdditionalInformationRequestPeriod/cbc:EndDate/text()",
            namespaces=namespaces,
        )
        end_time = part_element[0].xpath(
            "cac:TenderingProcess/cac:AdditionalInformationRequestPeriod/cbc:EndTime/text()",
            namespaces=namespaces,
        )

        if end_date and end_time:
            return convert_to_iso_format(end_date[0], end_time[0])

    return None


def convert_to_iso_format(date_string: str, time_string: str) -> str:
    """Convert separate date and time strings to ISO format datetime string.

    Args:
        date_string (str): The date string, potentially including timezone
        time_string (str): The time string, potentially including timezone

    Returns:
        str: Combined date and time in ISO format

    """
    # Make copies of the original strings
    date_part = date_string
    time_part = time_string

    # Extract timezone information
    date_timezone = ""
    if "+" in date_string:
        date_part, date_timezone = date_string.split("+", 1)
        date_timezone = "+" + date_timezone
    elif "-" in date_string[5:]:  # Check for timezone marker after YYYY-MM
        parts = date_string.split("-", 3)
        if len(parts) > 3:  # We have year-month-day-timezone
            date_part = "-".join(parts[0:3])
            date_timezone = "-" + parts[3]

    time_timezone = ""
    if "+" in time_string:
        time_part, time_timezone = time_string.split("+", 1)
        time_timezone = "+" + time_timezone
    elif "-" in time_string:
        parts = time_string.split("-", 1)
        time_part = parts[0]
        time_timezone = "-" + parts[1]

    # Handle Z timezone
    if date_string.endswith("Z"):
        date_part = date_string[:-1]
        date_timezone = "Z"
    if time_string.endswith("Z"):
        time_part = time_string[:-1]
        time_timezone = "Z"

    # Use the timezone from either date or time (preferring time if both have timezone)
    timezone = time_timezone or date_timezone

    # Extract microseconds if present in the time portion
    microseconds = ""
    if "." in time_part:
        time_base, microseconds = time_part.split(".", 1)
        time_part = time_base

    # Combine date and time
    datetime_string = f"{date_part}T{time_part}"

    # Parse the datetime
    date_time = datetime.fromisoformat(datetime_string)

    # Format the datetime with the timezone and microseconds
    if microseconds:
        base_datetime = date_time.isoformat().split(".")[0]
        result = f"{base_datetime}.{microseconds}"
    else:
        result = date_time.isoformat()

    # Add timezone if present
    if timezone:
        if timezone == "Z":
            return f"{result}Z"
        return f"{result}{timezone}"
    return result


def merge_additional_info_deadline_part(
    release_json: dict[str, Any], deadline: str | None
) -> None:
    """Merge part data containing additional information deadline into the release JSON.

    Args:
        release_json (Dict[str, Any]): The release JSON to update
        deadline (Optional[str]): ISO formatted datetime string for the enquiry period end date

    """
    if deadline:
        if "tender" not in release_json:
            release_json["tender"] = {}
        if "enquiryPeriod" not in release_json["tender"]:
            release_json["tender"]["enquiryPeriod"] = {}
        release_json["tender"]["enquiryPeriod"]["endDate"] = deadline
