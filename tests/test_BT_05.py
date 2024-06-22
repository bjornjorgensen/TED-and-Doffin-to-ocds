# test_BT_05.py
import pytest
from lxml import etree
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from converters.BT_05 import parse_notice_dispatch_date_time

def create_xml_content(issue_date, issue_time=None):
    """Helper function to create XML content for testing."""
    if issue_time:
        xml_content = f"""
        <root>
            <cbc:IssueDate xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">{issue_date}</cbc:IssueDate>
            <cbc:IssueTime xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">{issue_time}</cbc:IssueTime>
        </root>
        """
    else:
        xml_content = f"""
        <root>
            <cbc:IssueDate xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">{issue_date}</cbc:IssueDate>
        </root>
        """
    return xml_content.encode('utf-8')

def test_parse_notice_dispatch_date_time():
    # Test with valid date and time
    xml_content = create_xml_content('2020-10-21', '12:34:56+01:00')
    result = parse_notice_dispatch_date_time(xml_content)
    assert result == {"date": "2020-10-21T12:34:56+01:00"}

    # Test with valid date and no time (other date)
    xml_content = create_xml_content('2020-10-21')
    result = parse_notice_dispatch_date_time(xml_content)
    assert result == {"date": "2020-10-21T00:00:00Z"}

    # Test with invalid date
    xml_content = create_xml_content('invalid-date')
    result = parse_notice_dispatch_date_time(xml_content)
    assert result is None

    # Test with missing date
    xml_content = b"<root></root>"
    result = parse_notice_dispatch_date_time(xml_content)
    assert result is None

    # Test with valid date and invalid time
    xml_content = create_xml_content('2020-10-21', 'invalid-time')
    result = parse_notice_dispatch_date_time(xml_content)
    assert result is None

if __name__ == "__main__":
    pytest.main()