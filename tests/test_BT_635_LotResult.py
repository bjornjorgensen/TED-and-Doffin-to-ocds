# tests/test_BT_635_LotResult.py

import pytest
from lxml import etree
from converters.BT_635_LotResult import parse_buyer_review_requests_count, merge_buyer_review_requests_count
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_parse_buyer_review_requests_count():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
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
    </root>
    """
    
    result = parse_buyer_review_requests_count(xml_content)
    
    assert result is not None
    assert "statistics" in result
    assert len(result["statistics"]) == 1
    assert result["statistics"][0]["id"] == "1"
    assert result["statistics"][0]["value"] == 2
    assert result["statistics"][0]["scope"] == "complaints"
    assert result["statistics"][0]["relatedLot"] == "LOT-0001"

def test_merge_buyer_review_requests_count():
    release_json = {
        "statistics": [
            {
                "id": "1",
                "value": 1,
                "scope": "complaints",
                "relatedLot": "LOT-0001"
            }
        ]
    }
    
    buyer_review_requests_data = {
        "statistics": [
            {
                "id": "1",
                "value": 2,
                "scope": "complaints",
                "relatedLot": "LOT-0001"
            },
            {
                "id": "2",
                "value": 3,
                "scope": "complaints",
                "relatedLot": "LOT-0002"
            }
        ]
    }
    
    merge_buyer_review_requests_count(release_json, buyer_review_requests_data)
    
    assert len(release_json["statistics"]) == 2
    assert release_json["statistics"][0]["value"] == 2
    assert release_json["statistics"][1]["value"] == 3
    assert release_json["statistics"][1]["relatedLot"] == "LOT-0002"

def test_bt_635_lotresult_buyer_review_requests_count_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsNumeric>2</efbc:StatisticsNumeric>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsNumeric>3</efbc:StatisticsNumeric>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_buyer_review_requests.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "statistics" in result
    assert len(result["statistics"]) == 2
    
    lot_1_stat = next((stat for stat in result["statistics"] if stat["relatedLot"] == "LOT-0001"), None)
    assert lot_1_stat is not None
    assert lot_1_stat["value"] == 2
    assert lot_1_stat["scope"] == "complaints"

    lot_2_stat = next((stat for stat in result["statistics"] if stat["relatedLot"] == "LOT-0002"), None)
    assert lot_2_stat is not None
    assert lot_2_stat["value"] == 3
    assert lot_2_stat["scope"] == "complaints"

if __name__ == "__main__":
    pytest.main()