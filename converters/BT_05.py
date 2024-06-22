# BT_05.py
from lxml import etree
from datetime import datetime

def parse_notice_dispatch_date_time(xml_content):
    """
    Parses the XML content to extract the notice dispatch date and time,
    combines them into a single ISO formatted date string, and returns it.
    
    :param xml_content: The XML content as a string.
    :return: A dictionary containing the combined date and time in ISO format.
    """
    tree = etree.fromstring(xml_content)
    
    # Extract IssueDate and IssueTime
    issue_date_str = tree.xpath('string(/*/cbc:IssueDate)', namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
    issue_time_str = tree.xpath('string(/*/cbc:IssueTime)', namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
    
    if issue_date_str:
        # Check if the time component is missing
        if not issue_time_str:
            issue_time_str = '00:00:00Z'
        
        # Check for timezone in the date part
        if '+' in issue_date_str:
            date_part, timezone_part = issue_date_str.split('+')
            timezone_part = f'+{timezone_part}'
        else:
            date_part = issue_date_str
            timezone_part = 'Z'
        
        # Combine date and time into a single string
        combined_datetime_str = f"{date_part}T{issue_time_str}"
        
        # Append timezone if not already present in the time part
        if 'Z' not in issue_time_str and '+' not in issue_time_str:
            combined_datetime_str += timezone_part
        
        # Parse the combined string into a datetime object
        try:
            combined_datetime = datetime.fromisoformat(combined_datetime_str)
            # Convert back to ISO format string
            iso_format_str = combined_datetime.isoformat()
            # Ensure the timezone is 'Z' if it's UTC
            if '+00:00' in iso_format_str:
                iso_format_str = iso_format_str.replace('+00:00', 'Z')
            return {"date": iso_format_str}
        except ValueError as e:
            print(f"Error: Unable to parse combined date and time. Details: {e}")
            return None
    else:
        print("Error: IssueDate not found in XML.")
        return None