# utils/date_utils.py

import logging
from datetime import datetime, timezone
import re

logger = logging.getLogger(__name__)

def convert_to_iso_format(date_string, is_start_date=False):
    """
    Convert a date string to ISO 8601 format, following OCDS requirements.

    This function handles various input formats and ensures the output is
    compliant with OCDS date-time specifications. It adds default time and
    timezone information if not provided in the input.

    Args:
        date_string (str): The input date string to be converted.
        is_start_date (bool, optional): Flag to indicate if this is a start date.
            Defaults to False.

    Returns:
        str: The date-time string in ISO 8601 format.

    Raises:
        ValueError: If the input date_string is in an invalid format.

    Examples:
        >>> convert_to_iso_format("2019-11-19+01:00")
        '2019-11-19T23:59:59+01:00'
        >>> convert_to_iso_format("2019-11-15+01:00", is_start_date=True)
        '2019-11-15T00:00:00+01:00'
        >>> convert_to_iso_format("2019-11-19T14:30:00Z")
        '2019-11-19T14:30:00Z'
    """
    logger.debug(f"convert_to_iso_format input: {date_string}, is_start_date: {is_start_date}")
    
    # Regular expression to match various date-time formats
    date_format = r'(\d{4}-\d{2}-\d{2})(?:[T ](\d{2}:\d{2}:\d{2}))?(Z|[+-]\d{2}:?\d{2})?'

    match = re.match(date_format, date_string)
    if match:
        date_part, time_part, tz_part = match.groups()
        
        # If no time is provided, use start or end of day as default
        if not time_part:
            time_part = "00:00:00" if is_start_date else "23:59:59"
        elif len(time_part) == 5:
            time_part += ":00"  # Add seconds if missing
        
        # If no timezone is provided, use the original timezone or UTC as default
        if not tz_part:
            tz_part = "+01:00" if "+01:00" in date_string else "Z"
        elif tz_part != "Z" and ":" not in tz_part:
            tz_part = f"{tz_part[:3]}:{tz_part[3:]}"  # Add colon to timezone offset if missing
        
        # Construct ISO8601 compliant date-time string
        iso_date_string = f"{date_part}T{time_part}{tz_part}"
        
        # Parse the date-time string
        date = datetime.fromisoformat(iso_date_string.replace("Z", "+00:00"))
        
        # Format the date-time string according to ISO8601, preserving the original timezone
        return date.isoformat()
    
    # If no match is found, raise an error
    raise ValueError(f"Invalid date format: {date_string}")

def StartDate(date_string):
    """
    Convert a start date string to ISO 8601 format, following OCDS requirements.

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
    logger.debug(f"StartDate input: {date_string}")
    try:
        return convert_to_iso_format(date_string, is_start_date=True)
    except Exception as e:
        logger.error(f"Error parsing start date: {date_string}")
        logger.error(f"Exception: {str(e)}")
        raise ValueError(f"Invalid start date format: {date_string}")

def EndDate(date_string):
    """
    Convert an end date string to ISO 8601 format, following OCDS requirements.

    This function is specifically for handling end dates. It ensures that
    when only a date is provided, the time is set to 23:59:59 in the given timezone.

    Args:
        date_string (str): The input end date string to be converted.

    Returns:
        str: The end date-time string in ISO 8601 format.

    Raises:
        ValueError: If the input date_string is in an invalid format.

    Example:
        >>> EndDate("2019-11-19+01:00")
        '2019-11-19T23:59:59+01:00'
    """
    logger.debug(f"EndDate input: {date_string}")
    try:
        return convert_to_iso_format(date_string, is_start_date=False)
    except Exception as e:
        logger.error(f"Error parsing end date: {date_string}")
        logger.error(f"Exception: {str(e)}")
        raise ValueError(f"Invalid end date format: {date_string}")

# Additional utility functions can be added here as needed