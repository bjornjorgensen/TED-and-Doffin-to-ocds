import pytest
from lxml import etree
from converters.BT_127_notice import parse_future_notice_date, merge_future_notice_date

def test_parse_future_notice_date():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:PlannedDate>2020-03-15+01:00</cbc:PlannedDate>
    </root>
    """
    result = parse_future_notice_date(xml_content)
    assert result == "2020-03-15+01:00"

def test_parse_future_notice_date_with_time():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:PlannedDate>2020-03-15T10:30:00+01:00</cbc:PlannedDate>
    </root>
    """
    result = parse_future_notice_date(xml_content)
    assert result == "2020-03-15T10:30:00+01:00"

def test_parse_future_notice_date_invalid():
    xml_content = """
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:PlannedDate>invalid-date</cbc:PlannedDate>
    </root>
    """
    result = parse_future_notice_date(xml_content)
    assert result is None

def test_merge_future_notice_date_none():
    release_json = {}
    future_notice_date = None
    merge_future_notice_date(release_json, future_notice_date)
    assert release_json == {}