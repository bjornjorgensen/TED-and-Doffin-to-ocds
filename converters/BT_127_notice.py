# converters/BT_127_notice.py

from lxml import etree
import logging
from dateutil import parser

logger = logging.getLogger(__name__)

def parse_future_notice_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {}
    planned_date = root.xpath("//cbc:PlannedDate/text()", namespaces=namespaces)
    
    if planned_date:
        try:
            # Parse the date using dateutil.parser
            date_obj = parser.parse(planned_date[0])
            
            # Convert to ISO format
            iso_date = date_obj.isoformat()
            
            result = {
                "tender": {
                    "communication": {
                        "futureNoticeDate": iso_date
                    }
                }
            }
        except ValueError as e:
            logger.error(f"Error parsing PlannedDate: {e}")

    return result if result else None

def merge_future_notice_date(release_json, future_notice_data):
    if not future_notice_data:
        logger.warning("No Future Notice Date data to merge")
        return

    tender = release_json.setdefault("tender", {})
    communication = tender.setdefault("communication", {})
    communication["futureNoticeDate"] = future_notice_data["tender"]["communication"]["futureNoticeDate"]

    logger.info(f"Merged Future Notice Date: {communication['futureNoticeDate']}")