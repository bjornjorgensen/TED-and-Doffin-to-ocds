from ted_and_doffin_to_ocds.converters.bt_760_lotresult import (
    parse_received_submissions_type,
    merge_received_submissions_type,
)


def test_parse_received_submissions_type():
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
                    <efbc:StatisticsCode listName="received-submission-type">t-esubm</efbc:StatisticsCode>
                </efac:ReceivedSubmissionsStatistics>
            </efac:LotResult>
        </efac:noticeResult>
    </root>
    """
    result = parse_received_submissions_type(xml_content)
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    stat = result["bids"]["statistics"][0]
    assert stat["id"] == "electronicBids-LOT-0001"
    assert stat["measure"] == "electronicBids"
    assert stat["relatedLots"] == ["LOT-0001"]


def test_merge_received_submissions_type():
    release_json = {"bids": {"statistics": []}}
    received_submissions_type_data = {
        "bids": {
            "statistics": [
                {
                    "id": "electronicBids-LOT-0001",
                    "measure": "electronicBids",
                    "relatedLots": ["LOT-0001"],
                },
            ],
        },
    }
    merge_received_submissions_type(release_json, received_submissions_type_data)
    assert len(release_json["bids"]["statistics"]) == 1
    stat = release_json["bids"]["statistics"][0]
    assert stat["id"] == "1"
    assert stat["measure"] == "electronicBids"
    assert stat["relatedLots"] == ["LOT-0001"]