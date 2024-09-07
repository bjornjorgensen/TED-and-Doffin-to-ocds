# tests/test_BT_330_Procedure.py

import pytest
from lxml import etree
from converters.BT_330_Procedure import parse_group_identifier, merge_group_identifier


def test_parse_group_identifier():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:LotDistribution>
                <cac:LotsGroup>
                    <cbc:LotsGroupID schemeName="LotsGroup">GLO-0001</cbc:LotsGroupID>
                </cac:LotsGroup>
            </cac:LotDistribution>
        </cac:TenderingTerms>
    </root>
    """
    result = parse_group_identifier(xml_content)
    assert result == {"tender": {"lotGroups": [{"id": "GLO-0001"}]}}


def test_merge_group_identifier():
    release_json = {"tender": {"lotGroups": [{"id": "GLO-0002"}]}}
    group_identifier_data = {
        "tender": {"lotGroups": [{"id": "GLO-0001"}, {"id": "GLO-0002"}]}
    }
    merge_group_identifier(release_json, group_identifier_data)
    assert release_json == {
        "tender": {"lotGroups": [{"id": "GLO-0002"}, {"id": "GLO-0001"}]}
    }


def test_parse_group_identifier_missing():
    xml_content = "<root></root>"
    result = parse_group_identifier(xml_content)
    assert result is None


def test_merge_group_identifier_empty():
    release_json = {}
    group_identifier_data = {"tender": {"lotGroups": [{"id": "GLO-0001"}]}}
    merge_group_identifier(release_json, group_identifier_data)
    assert release_json == {"tender": {"lotGroups": [{"id": "GLO-0001"}]}}
