from lxml import etree
from datetime import datetime, timezone

def parse_notice_preferred_publication_date(xml_content):
    root = etree.fromstring(xml_content)
    namespaces = {
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    requested_publication_date = root.xpath("/*/cbc:RequestedPublicationDate/text()", namespaces=namespaces)
    
    if requested_publication_date:
        date_str = requested_publication_date[0]
        
        # Parse the date
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            # If parsing fails, try without time component
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                # Add time component based on whether it's an end date
                if date.time() == datetime.min.time():
                    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    date = date.replace(hour=23, minute=59, second=59, microsecond=0)
            except ValueError:
                # If parsing fails again, return None
                return None

        # Format the date
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        
        return date.isoformat()
    
    return None

def merge_notice_preferred_publication_date(release_json, preferred_publication_date):
    if preferred_publication_date:
        tender = release_json.setdefault("tender", {})
        communication = tender.setdefault("communication", {})
        communication["noticePreferredPublicationDate"] = preferred_publication_date
    
    return release_json