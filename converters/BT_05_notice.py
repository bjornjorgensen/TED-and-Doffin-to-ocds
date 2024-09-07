# converters/BT_05_Notice.py

import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)


def parse_notice_dispatch_date_time(xml_content):
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
