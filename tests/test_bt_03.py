# tests/test_bt_03.py

import pytest
from lxml import etree
from ted_and_doffin_to_ocds.converters.bt_03 import parse_form_type, merge_form_type

def create_xml(list_name):
    return f"""
    <root xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:NoticeTypeCode listName="{list_name}">cn-standard</cbc:NoticeTypeCode>
    </root>
    """

@pytest.mark.parametrize("list_name, expected", [
    ("planning", {"tag": ["tender"], "tender": {"status": "planned"}}),
    ("competition", {"tag": ["tender"], "tender": {"status": "active"}}),
    ("change", {"tag": ["tenderUpdate"]}),
    ("result", {"tag": ["award", "contract"], "tender": {"status": "complete"}}),
    ("dir-awa-pre", {"tag": ["award", "contract"], "tender": {"status": "complete"}}),
    ("cont-modif", {"tag": ["awardUpdate", "contractUpdate"]}),
])
def test_parse_form_type(list_name, expected):
    xml_content = create_xml(list_name)
    result = parse_form_type(xml_content)
    assert result == expected

def test_parse_form_type_unknown_type():
    xml_content = create_xml("unknown")
    result = parse_form_type(xml_content)
    assert result is None

def test_parse_form_type_no_notice_type_code():
    xml_content = "<root></root>"
    result = parse_form_type(xml_content)
    assert result is None

@pytest.mark.parametrize("form_type_data, initial_release, expected_release", [
    (
        {"tag": ["tender"], "tender": {"status": "active"}},
        {},
        {"tag": ["tender"], "tender": {"status": "active"}}
    ),
    (
        {"tag": ["award", "contract"], "tender": {"status": "complete"}},
        {"tender": {"title": "Test Tender"}},
        {"tag": ["award", "contract"], "tender": {"title": "Test Tender", "status": "complete"}}
    ),
    (
        {"tag": ["tenderUpdate"]},
        {"tag": ["tender"], "tender": {"status": "active"}},
        {"tag": ["tenderUpdate"], "tender": {"status": "active"}}
    ),
])
def test_merge_form_type(form_type_data, initial_release, expected_release):
    merge_form_type(initial_release, form_type_data)
    assert initial_release == expected_release

def test_merge_form_type_no_data():
    release_json = {"tender": {"title": "Test Tender"}}
    original_release = release_json.copy()
    merge_form_type(release_json, None)
    assert release_json == original_release