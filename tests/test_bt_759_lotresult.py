from src.ted_and_doffin_to_ocds.converters.eforms.bt_759_lotresult import (
    merge_received_submissions_count,
    parse_received_submissions_count,
)


def test_parse_received_submissions_count() -> None:
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:noticeResult>
            <efac:LotResult>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
                <efac:ReceivedSubmissionsStatistics>
                    <efbc:StatisticsNumeric>5</efbc:StatisticsNumeric>
                </efac:ReceivedSubmissionsStatistics>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    result = parse_received_submissions_count(xml_content)
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    stat = result["bids"]["statistics"][0]
    assert stat["id"] == "bids-LOT-0001"
    assert stat["measure"] == "bids"
    assert stat["value"] == 5
    assert stat["relatedLots"] == ["LOT-0001"]


def test_merge_received_submissions_count() -> None:
    release_json = {"bids": {"statistics": []}}
    received_submissions_data = {
        "bids": {
            "statistics": [
                {
                    "id": "bids-LOT-0001",
                    "measure": "bids",
                    "value": 5,
                    "relatedLots": ["LOT-0001"],
                },
            ],
        },
    }
    merge_received_submissions_count(release_json, received_submissions_data)
    assert len(release_json["bids"]["statistics"]) == 1
    stat = release_json["bids"]["statistics"][0]
    assert stat["id"] == "1"
    assert stat["measure"] == "bids"
    assert stat["value"] == 5
    assert stat["relatedLots"] == ["LOT-0001"]
