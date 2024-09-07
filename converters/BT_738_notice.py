# converters/BT_738_notice.py

import logging
from lxml import etree
from utils.date_utils import StartDate

logger = logging.getLogger(__name__)


def parse_notice_preferred_publication_date(xml_content):
    """
    Parse the XML content to extract the notice preferred publication date.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed notice preferred publication date.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
    }

    xpath_query = "/*/cbc:RequestedPublicationDate"
    requested_publication_date = root.xpath(xpath_query, namespaces=namespaces)

    if requested_publication_date:
        date_str = requested_publication_date[0].text
        try:
            # Use StartDate function from date_utils to convert the date
            formatted_date = StartDate(date_str)

            return {
                "tender": {
                    "communication": {"noticePreferredPublicationDate": formatted_date}
                }
            }
        except ValueError as e:
            logger.error(f"Error parsing date: {e}")
            return None

    return None


def merge_notice_preferred_publication_date(
    release_json, preferred_publication_date_data
):
    """
    Merge the parsed notice preferred publication date into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        preferred_publication_date_data (dict): The parsed notice preferred publication date data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not preferred_publication_date_data:
        logger.warning("No notice preferred publication date data to merge")
        return

    tender = release_json.setdefault("tender", {})
    communication = tender.setdefault("communication", {})
    communication["noticePreferredPublicationDate"] = preferred_publication_date_data[
        "tender"
    ]["communication"]["noticePreferredPublicationDate"]

    logger.info("Merged notice preferred publication date data")
