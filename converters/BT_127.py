from lxml import etree
from datetime import datetime, timezone

def parse_future_notice_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    planned_date = root.xpath("//cbc:PlannedDate/text()", namespaces=namespaces)
    
    if planned_date:
        date_str = planned_date[0]
        
        # Parse the date
        try:
            date = datetime.fromisoformat(date_str)
        except ValueError:
            # If fromisoformat fails, try a more lenient parsing
            date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # If there's no time component, add it
        if date.hour == 0 and date.minute == 0 and date.second == 0:
            date = date.replace(hour=0, minute=0, second=0)
        
        # If there's no timezone info, assume UTC
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        
        # Format the date according to ISO 8601
        formatted_date = date.isoformat()
        
        return {
            "tender": {
                "communication": {
                    "futureNoticeDate": formatted_date
                }
            }
        }
    
    return None