# converters/BT_127_Notice.py

import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)

def parse_future_notice_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
    
    planned_date = root.xpath("/*/cbc:PlannedDate/text()", namespaces=namespaces)
    if planned_date:
        return convert_to_iso_format(planned_date[0])
    return None

def convert_to_iso_format(date_string):
    # Split the date string and timezone
    date_part, _, tz_part = date_string.partition('+')
    
    # Parse the date part
    date = datetime.strptime(date_part, "%Y-%m-%d")
    
    # Add time component
    date = date.replace(hour=0, minute=0, second=0)
    
    # Format the date with the original timezone
    return f"{date.isoformat()}+{tz_part}"

def merge_future_notice_date(release_json, future_notice_date):
    if future_notice_date:
        if "tender" not in release_json:
            release_json["tender"] = {}
        if "communication" not in release_json["tender"]:
            release_json["tender"]["communication"] = {}
        release_json["tender"]["communication"]["futureNoticeDate"] = future_notice_date