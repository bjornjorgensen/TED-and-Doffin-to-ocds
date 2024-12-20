import logging
import re

logger = logging.getLogger(__name__)

DATE_FORMAT = (
    r"(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}:\d{2}(?:\.\d+)?))?([Z]|[+-]\d{2}:?\d{2})?"
)


def parse_date_parts(date_string: str) -> tuple[str, str | None, str | None]:
    match = re.match(DATE_FORMAT, date_string)
    if not match:
        error_message = f"Invalid date format: {date_string}"
        raise ValueError(error_message)
    return match.groups()


def format_timezone(tz_part: str | None, original_date: str) -> str:
    if not tz_part:
        return "+01:00" if "+01:00" in original_date else "Z"
    if tz_part != "Z" and ":" not in tz_part:
        return f"{tz_part[:3]}:{tz_part[3:]}"
    return tz_part


def convert_to_iso_format(date_string: str, is_start_date: bool = False) -> str:
    logger.debug(
        "convert_to_iso_format input: %s, is_start_date: %s",
        date_string,
        is_start_date,
    )

    try:
        date_part, time_part, tz_part = parse_date_parts(date_string)

        time_part = time_part or ("00:00:00" if is_start_date else "23:59:59")
        tz_part = format_timezone(tz_part, date_string)

        iso_date_string = f"{date_part}T{time_part}{tz_part}"

        logger.debug("convert_to_iso_format output: %s", iso_date_string)
    except ValueError as e:
        logger.exception("Error parsing date: %s", date_string)
        error_message = f"Invalid date format: {date_string}"
        raise ValueError(error_message) from e
    else:
        return iso_date_string


def start_date(date_string: str) -> str:
    """Convert a start date string to ISO 8601 format, following OCDS requirements.

    This function is specifically for handling start dates. It ensures that
    when only a date is provided, the time is set to 00:00:00 in the given timezone.

    Args:
        date_string (str): The input start date string to be converted.

    Returns:
        str: The start date-time string in ISO 8601 format.

    Raises:
        ValueError: If the input date_string is in an invalid format.

    Example:
        >>> StartDate("2019-11-15+01:00")
        '2019-11-15T00:00:00+01:00'

    """
    logger.debug("StartDate input: %s", date_string)
    try:
        return convert_to_iso_format(date_string, is_start_date=True)
    except ValueError as e:
        logger.exception("Error parsing start date: %s", date_string)
        error_message = f"Invalid start date format: {date_string}"
        raise ValueError(error_message) from e


def end_date(date_string: str) -> str:
    """Convert an end date string to ISO 8601 format, following OCDS requirements.

    This function is specifically for handling end dates. It ensures that
    when only a date is provided, the time is set to 23:59:59 in the given timezone.

    Args:
        date_string (str): The input end date string to be converted.

    Returns:
        str: The end date-time string in ISO 8601 format.

    Raises:
        ValueError: If the input date_string is in an invalid format.

    Example:
        >>> EndDate("2019-11-15+01:00")
        '2019-11-15T23:59:59+01:00'

    """
    logger.debug("EndDate input: %s", date_string)
    try:
        result = convert_to_iso_format(date_string, is_start_date=False)
        logger.debug("EndDate result: %s", result)
    except ValueError as e:
        logger.exception("Error parsing end date: %s", date_string)
        error_message = f"Invalid end date format: {date_string}"
        raise ValueError(error_message) from e
    else:
        return result
