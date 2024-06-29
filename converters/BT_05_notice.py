# converters/BT_05_notice.py

from lxml import etree
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def parse_notice_dispatch_datetime(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    issue_date = root.xpath("/*/cbc:IssueDate/text()", namespaces=namespaces)
    issue_time = root.xpath("/*/cbc:IssueTime/text()", namespaces=namespaces)

    if issue_date and issue_time:
        try:
            # Remove the timezone information from the date string
            date_str = issue_date[0].split('+')[0]
            # Combine date and time
            datetime_str = f"{date_str}T{issue_time[0]}"
            # Parse the combined string to a datetime object
            dispatch_datetime = datetime.fromisoformat(datetime_str)
            # Convert to ISO format
            iso_datetime = dispatch_datetime.isoformat()
            
            return {"date": iso_datetime}
        except ValueError as e:
            logger.error(f"Error parsing datetime: {e}")
            return None
    else:
        logger.warning("Missing IssueDate or IssueTime in XML")
        return None

def merge_notice_dispatch_datetime(release_json, dispatch_datetime_data):
    if not dispatch_datetime_data:
        logger.warning("No Notice Dispatch Date and Time data to merge")
        return

    release_json["date"] = dispatch_datetime_data["date"]
    logger.info("Merged Notice Dispatch Date and Time")