# converters/BT_05_Notice.py

import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)

def parse_notice_dispatch_date_time(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}
    
    issue_date = root.xpath("/*/cbc:IssueDate/text()", namespaces=namespaces)
    issue_time = root.xpath("/*/cbc:IssueTime/text()", namespaces=namespaces)
    
    if issue_date and issue_time:
        return convert_to_iso_format(issue_date[0], issue_time[0])
    return None

def convert_to_iso_format(date_string, time_string):
    # Combine date and time
    datetime_string = f"{date_string.split('+')[0]}T{time_string}"
    
    # Parse the datetime
    date_time = datetime.fromisoformat(datetime_string)
    
    # Format the datetime with the original timezone
    return date_time.isoformat()

def merge_notice_dispatch_date_time(release_json, dispatch_date_time):
    if dispatch_date_time:
        release_json["date"] = dispatch_date_time