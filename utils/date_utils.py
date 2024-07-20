# utils/date_utils.py

from datetime import datetime
def convert_to_iso_format(date_string):
    # Split the date string and timezone
    date_part, _, tz_part = date_string.partition('+')
    # Parse the date part
    date = datetime.strptime(date_part, "%Y-%m-%d")
    # Add time component
    date = date.replace(hour=0, minute=0, second=0)
    # Format the date with the original timezone
    if tz_part:
        return f"{date.isoformat()}+{tz_part}"
    else:
        return f"{date.isoformat()}Z"