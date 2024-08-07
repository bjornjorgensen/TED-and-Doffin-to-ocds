# tests/test_BT_759_LotResult.py

import pytest
from lxml import etree
from converters.BT_759_LotResult import parse_received_submissions_count, merge_received_submissions_count

def test_parse_received_submissions_count():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:ReceivedSubmissionsStatistics>
                    <efbc:StatisticsNumeric>12</efbc:StatisticsNumeric>
                </efac:ReceivedSubmissionsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    
    result = parse_received_submissions_count(xml_content)
    
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    assert result["bids"]["statistics"][0]["id"] == "1"
    assert result["bids"]["statistics"][0]["value"] == 12
    assert result["bids"]["statistics"][0]["relatedLot"] == "LOT-0001"

def test_merge_received_submissions_count():
    release_json = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "value": 10,
                    "relatedLot": "LOT-0001"
                }
            ]
        }
    }
    
    received_submissions_data = {
        "bids": {
            "statistics": [
                {
                    "id": "2",
                    "value": 12,
                    "relatedLot": "LOT-0001"
                },
                {
                    "id": "3",
                    "value": 8,
                    "relatedLot": "LOT-0002"
                }
            ]
        }
    }
    
    merge_received_submissions_count(release_json, received_submissions_data)
    
    assert len(release_json["bids"]["statistics"]) == 2
    assert release_json["bids"]["statistics"][0]["value"] == 12
    assert release_json["bids"]["statistics"][0]["relatedLot"] == "LOT-0001"
    assert release_json["bids"]["statistics"][1]["value"] == 8
    assert release_json["bids"]["statistics"][1]["relatedLot"] == "LOT-0002"

if __name__ == "__main__":
    pytest.main()