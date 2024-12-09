# converters/bt_127_notice.py

import logging

from lxml import etree

from ted_and_doffin_to_ocds.utils.date_utils import start_date

logger = logging.getLogger(__name__)


def parse_future_notice_date(xml_content: str | bytes) -> str | None:
    """Parse the future notice date from XML content.

    Args:
        xml_content (Union[str, bytes]): The XML content containing the planned date

    Returns:
        Optional[str]: ISO formatted date string with timezone, or None if not found
        Format example: "2020-03-15T00:00:00+01:00"

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

    planned_date = root.xpath("/*/cbc:PlannedDate/text()", namespaces=namespaces)
    if planned_date:
        try:
            return start_date(planned_date[0])
        except ValueError as e:
            logger.warning("Error parsing planned date: %s", e)
            return None
    return None


def merge_future_notice_date(
    release_json: dict, future_notice_date: str | None
) -> None:
    """Merge future notice date into the release JSON.

    Args:
        release_json (dict): The target release JSON to merge data into
        future_notice_date (Optional[str]): ISO formatted date string to be merged

    """
    if future_notice_date:
        if "tender" not in release_json:
            release_json["tender"] = {}
        if "communication" not in release_json["tender"]:
            release_json["tender"]["communication"] = {}
        release_json["tender"]["communication"]["futureNoticeDate"] = future_notice_date
