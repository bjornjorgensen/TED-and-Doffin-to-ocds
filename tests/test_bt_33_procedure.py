# tests/test_bt_33_procedure.py

from ted_and_doffin_to_ocds.converters.bt_33_procedure import (
    parse_max_lots_awarded,
    merge_max_lots_awarded,
)


def test_parse_max_lots_awarded():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:LotDistribution>
            <cbc:MaximumLotsAwardedNumeric>4</cbc:MaximumLotsAwardedNumeric>
        </cac:LotDistribution>
    </root>
    """
    result = parse_max_lots_awarded(xml_content)
    assert result == {"tender": {"lotDetails": {"maximumLotsAwardedPerSupplier": 4}}}


def test_merge_max_lots_awarded():
    release_json = {}
    max_lots_awarded_data = {
        "tender": {"lotDetails": {"maximumLotsAwardedPerSupplier": 4}},
    }
    merge_max_lots_awarded(release_json, max_lots_awarded_data)
    assert release_json == {
        "tender": {"lotDetails": {"maximumLotsAwardedPerSupplier": 4}},
    }


def test_parse_max_lots_awarded_missing():
    xml_content = "<root></root>"
    result = parse_max_lots_awarded(xml_content)
    assert result is None


def test_parse_max_lots_awarded_invalid():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:LotDistribution>
            <cbc:MaximumLotsAwardedNumeric>invalid</cbc:MaximumLotsAwardedNumeric>
        </cac:LotDistribution>
    </root>
    """
    result = parse_max_lots_awarded(xml_content)
    assert result is None
