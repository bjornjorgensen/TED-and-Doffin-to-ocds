# tests/test_BT_711_LotResult.py

import pytest
from lxml import etree
from converters.BT_711_LotResult import parse_tender_value_highest, merge_tender_value_highest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_parse_tender_value_highest():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:HigherTenderAmount currencyID="EUR">456</cbc:HigherTenderAmount>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    
    result = parse_tender_value_highest(xml_content)
    
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    assert result["bids"]["statistics"][0]["measure"] == "highestValidBidValue"
    assert result["bids"]["statistics"][0]["value"] == 456
    assert result["bids"]["statistics"][0]["currency"] == "EUR"
    assert result["bids"]["statistics"][0]["relatedLot"] == "LOT-0001"

def test_merge_tender_value_highest():
    release_json = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "measure": "validBids",
                    "value": 5
                }
            ]
        }
    }
    
    tender_value_highest_data = {
        "bids": {
            "statistics": [
                {
                    "id": "2",
                    "measure": "highestValidBidValue",
                    "value": 456,
                    "currency": "EUR",
                    "relatedLot": "LOT-0001"
                }
            ]
        }
    }
    
    merge_tender_value_highest(release_json, tender_value_highest_data)
    
    assert len(release_json["bids"]["statistics"]) == 2
    assert release_json["bids"]["statistics"][1]["measure"] == "highestValidBidValue"
    assert release_json["bids"]["statistics"][1]["value"] == 456
    assert release_json["bids"]["statistics"][1]["currency"] == "EUR"
    assert release_json["bids"]["statistics"][1]["relatedLot"] == "LOT-0001"

def test_bt_711_lot_result_highest_tender_value_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:HigherTenderAmount currencyID="EUR">456</cbc:HigherTenderAmount>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
            <efac:LotResult>
                <cbc:HigherTenderAmount currencyID="USD">789</cbc:HigherTenderAmount>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_highest_tender_value.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "bids" in result
    assert "statistics" in result["bids"]
    
    highest_tender_value_stats = [stat for stat in result["bids"]["statistics"] if stat["measure"] == "highestValidBidValue"]
    assert len(highest_tender_value_stats) == 2

    lot_1_stat = next((stat for stat in highest_tender_value_stats if stat["relatedLot"] == "LOT-0001"), None)
    assert lot_1_stat is not None
    assert lot_1_stat["value"] == 456
    assert lot_1_stat["currency"] == "EUR"

    lot_2_stat = next((stat for stat in highest_tender_value_stats if stat["relatedLot"] == "LOT-0002"), None)
    assert lot_2_stat is not None
    assert lot_2_stat["value"] == 789
    assert lot_2_stat["currency"] == "USD"

if __name__ == "__main__":
    pytest.main()