from datetime import datetime

def convert_to_iso_format(date_string, is_start_date=True):
    """
    Convert a given date string to ISO 8601 format.
    If a time component is missing from a date, use 'T23:59:59Z' for end dates and 'T00:00:00Z' for other dates.
    If a timezone component is present in the date (e.g. '+02:00'), preserve it. Otherwise, use the UTC timezone 'Z'.
    """
    try:
        if '+' in date_string or '-' in date_string[10:]:  # Check for timezone
            date_obj = datetime.fromisoformat(date_string)
        else:
            date_obj = datetime.strptime(date_string, "%Y-%m-%d")

        if date_obj.time() == datetime.min.time():
            if is_start_date:
                return date_obj.strftime("%Y-%m-%dT00:00:00") + 'Z'
            else:
                return date_obj.strftime("%Y-%m-%dT23:59:59") + 'Z'
        return date_obj.isoformat() + 'Z' if 'Z' not in date_string and '+' not in date_string else date_obj.isoformat()
    except Exception as e:
        print(f"Error converting date: {e}")
        return None
