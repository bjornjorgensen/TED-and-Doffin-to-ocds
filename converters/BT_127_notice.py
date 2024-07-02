import logging
from datetime import datetime
from lxml import etree

logger = logging.getLogger(__name__)

def parse_future_notice_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    planned_date = root.xpath('//cbc:PlannedDate/text()', namespaces=namespaces)
    
    if planned_date:
        date_str = planned_date[0]
        try:
            # Try to parse the date to validate it
            datetime.fromisoformat(date_str)
            return date_str
        except ValueError:
            logger.warning(f"Invalid date format: {date_str}")
            return None
    
    return None

def merge_future_notice_date(release_json, future_notice_date):
    if future_notice_date:
        if 'tender' not in release_json:
            release_json['tender'] = {}
        if 'communication' not in release_json['tender']:
            release_json['tender']['communication'] = {}
        release_json['tender']['communication']['futureNoticeDate'] = future_notice_date
        logger.info(f"Merged future notice date: {future_notice_date}")
    else:
        logger.warning("No future notice date to merge")