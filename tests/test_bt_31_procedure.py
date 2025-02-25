# tests/test_bt_31_procedure.py

from src.ted_and_doffin_to_ocds.converters.eforms.bt_31_procedure import (
    merge_max_lots_allowed,
    parse_max_lots_allowed,
)


def test_parse_max_lots_allowed() -> None:
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


def test_merge_max_lots_allowed() -> None:
    release_json = {}
    max_lots_data = {"tender": {"lotDetails": {"maximumLotsBidPerSupplier": 6}}}
    merge_max_lots_allowed(release_json, max_lots_data)
    assert release_json == {"tender": {"lotDetails": {"maximumLotsBidPerSupplier": 6}}}


def test_parse_max_lots_allowed_missing() -> None:
    xml_content = "<root></root>"
    result = parse_max_lots_allowed(xml_content)
    assert result is None


def test_merge_max_lots_allowed_empty() -> None:
    release_json = {}
    merge_max_lots_allowed(release_json, None)
    assert release_json == {}
