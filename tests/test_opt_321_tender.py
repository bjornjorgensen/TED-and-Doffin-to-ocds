# tests/test_opt_321_tender.py

from ted_and_doffin_to_ocds.converters.opt_321_tender import (
    merge_tender_technical_identifier,
    parse_tender_technical_identifier,
)


def test_parse_tender_technical_identifier() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotTender>
                <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
            </efac:LotTender>
        </efac:NoticeResult>
    </root>
    """
    result = parse_tender_technical_identifier(xml_content)
    assert result == {"bids": {"details": [{"id": "TEN-0001"}]}}


def test_merge_tender_technical_identifier() -> None:
    release_json = {
        "bids": {"details": [{"id": "TEN-0002", "value": {"amount": 1000}}]}
    }
    tender_technical_identifier_data = {"bids": {"details": [{"id": "TEN-0001"}]}}
    merge_tender_technical_identifier(release_json, tender_technical_identifier_data)
    assert release_json == {
        "bids": {
            "details": [
                {"id": "TEN-0002", "value": {"amount": 1000}},
                {"id": "TEN-0001"},
            ]
        }
    }


def test_merge_tender_technical_identifier_existing_bid() -> None:
    release_json = {
        "bids": {"details": [{"id": "TEN-0001", "value": {"amount": 1000}}]}
    }
    tender_technical_identifier_data = {"bids": {"details": [{"id": "TEN-0001"}]}}
    merge_tender_technical_identifier(release_json, tender_technical_identifier_data)
    assert release_json == {
        "bids": {"details": [{"id": "TEN-0001", "value": {"amount": 1000}}]}
    }


def test_merge_tender_technical_identifier_no_data() -> None:
    release_json = {
        "bids": {"details": [{"id": "TEN-0001", "value": {"amount": 1000}}]}
    }
    merge_tender_technical_identifier(release_json, None)
    assert release_json == {
        "bids": {"details": [{"id": "TEN-0001", "value": {"amount": 1000}}]}
    }
