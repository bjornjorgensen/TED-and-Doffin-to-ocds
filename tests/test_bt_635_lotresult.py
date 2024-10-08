# tests/test_bt_635_lotresult.py

from ted_and_doffin_to_ocds.converters.bt_635_lotresult import (
    parse_buyer_review_requests_count,
    merge_buyer_review_requests_count,
)


def test_parse_buyer_review_requests_count():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efext:EformsExtension>
            <efac:NoticeResult>
                <efac:LotResult>
                    <efac:AppealRequestsStatistics>
                        <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                    </efac:AppealRequestsStatistics>
                    <efac:TenderLot>
                        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                    </efac:TenderLot>
                </efac:LotResult>
            </efac:NoticeResult>
        </efext:EformsExtension>
    </root>
    """

    result = parse_buyer_review_requests_count(xml_content)
    assert result == {
        "statistics": [{"value": 2.0, "scope": "complaints", "relatedLot": "LOT-0001"}]
    }


def test_merge_buyer_review_requests_count():
    release_json = {
        "statistics": [
            {"id": "1", "scope": "complaints", "relatedLot": "LOT-0001", "value": 1.0}
        ]
    }

    buyer_review_requests_count_data = {
        "statistics": [{"value": 2.0, "scope": "complaints", "relatedLot": "LOT-0001"}]
    }

    merge_buyer_review_requests_count(release_json, buyer_review_requests_count_data)

    assert release_json == {
        "statistics": [
            {"id": "1", "scope": "complaints", "relatedLot": "LOT-0001", "value": 2.0}
        ]
    }


def test_merge_buyer_review_requests_count_new_statistic():
    release_json = {
        "statistics": [
            {"id": "1", "scope": "complaints", "relatedLot": "LOT-0001", "value": 1.0}
        ]
    }

    buyer_review_requests_count_data = {
        "statistics": [{"value": 3.0, "scope": "complaints", "relatedLot": "LOT-0002"}]
    }

    merge_buyer_review_requests_count(release_json, buyer_review_requests_count_data)

    assert release_json == {
        "statistics": [
            {"id": "1", "scope": "complaints", "relatedLot": "LOT-0001", "value": 1.0},
            {"id": "2", "value": 3.0, "scope": "complaints", "relatedLot": "LOT-0002"},
        ]
    }


def test_merge_buyer_review_requests_count_multiple_notices():
    # Simulating multiple notices
    release_json = {
        "statistics": [
            {"id": "1", "scope": "complaints", "relatedLot": "LOT-0001", "value": 1.0},
            {"id": "2", "scope": "complaints", "relatedLot": "LOT-0002", "value": 2.0},
            {"id": "3", "scope": "other", "relatedLot": "LOT-0003", "value": 3.0},
            {"id": "9", "scope": "complaints", "relatedLot": "LOT-0004", "value": 4.0},
        ]
    }

    buyer_review_requests_count_data = {
        "statistics": [
            {"value": 5.0, "scope": "complaints", "relatedLot": "LOT-0005"},
            {"value": 6.0, "scope": "complaints", "relatedLot": "LOT-0006"},
        ]
    }

    merge_buyer_review_requests_count(release_json, buyer_review_requests_count_data)

    assert release_json == {
        "statistics": [
            {"id": "1", "scope": "complaints", "relatedLot": "LOT-0001", "value": 1.0},
            {"id": "2", "scope": "complaints", "relatedLot": "LOT-0002", "value": 2.0},
            {"id": "3", "scope": "other", "relatedLot": "LOT-0003", "value": 3.0},
            {"id": "9", "scope": "complaints", "relatedLot": "LOT-0004", "value": 4.0},
            {"id": "10", "value": 5.0, "scope": "complaints", "relatedLot": "LOT-0005"},
            {"id": "11", "value": 6.0, "scope": "complaints", "relatedLot": "LOT-0006"},
        ]
    }
