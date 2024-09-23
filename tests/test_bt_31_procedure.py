# tests/test_bt_31_procedure.py

from ted_and_doffin_to_ocds.converters.bt_31_procedure import (
    parse_max_lots_allowed,
    merge_max_lots_allowed,
)


def test_parse_max_lots_allowed():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingTerms>
            <cac:LotDistribution>
                <cbc:MaximumLotsSubmittedNumeric>6</cbc:MaximumLotsSubmittedNumeric>
            </cac:LotDistribution>
        </cac:TenderingTerms>
    </root>
    """
    result = parse_max_lots_allowed(xml_content)
    assert result == {"tender": {"lotDetails": {"maximumLotsBidPerSupplier": 6}}}


def test_merge_max_lots_allowed():
    release_json = {}
    max_lots_data = {"tender": {"lotDetails": {"maximumLotsBidPerSupplier": 6}}}
    merge_max_lots_allowed(release_json, max_lots_data)
    assert release_json == {"tender": {"lotDetails": {"maximumLotsBidPerSupplier": 6}}}


def test_parse_max_lots_allowed_missing():
    xml_content = "<root></root>"
    result = parse_max_lots_allowed(xml_content)
    assert result is None


def test_merge_max_lots_allowed_empty():
    release_json = {}
    merge_max_lots_allowed(release_json, None)
    assert release_json == {}
