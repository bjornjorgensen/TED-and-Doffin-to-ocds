# converters/bt_13_part.py

import logging
from datetime import datetime

from lxml import etree

logger = logging.getLogger(__name__)


def parse_additional_info_deadline_part(xml_content):
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
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
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


def convert_to_iso_format(date_string, time_string):
    # Combine date and time
    datetime_string = f"{date_string.split('+')[0]}T{time_string}"

    # Parse the datetime
    date_time = datetime.fromisoformat(datetime_string)

    # Format the datetime with the original timezone
    return date_time.isoformat()


def merge_additional_info_deadline_part(release_json, deadline) -> None:
    if deadline:
        if "tender" not in release_json:
            release_json["tender"] = {}
        if "enquiryPeriod" not in release_json["tender"]:
            release_json["tender"]["enquiryPeriod"] = {}
        release_json["tender"]["enquiryPeriod"]["endDate"] = deadline
