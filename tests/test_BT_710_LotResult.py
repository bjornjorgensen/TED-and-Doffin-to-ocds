# tests/test_BT_710_LotResult.py

import pytest
from lxml import etree
from converters.BT_710_LotResult import parse_tender_value_lowest, merge_tender_value_lowest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_parse_tender_value_lowest():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:LowerTenderAmount currencyID="EUR">1230000</cbc:LowerTenderAmount>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    
    result = parse_tender_value_lowest(xml_content)
    
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    assert result["bids"]["statistics"][0]["id"] == "1"
    assert result["bids"]["statistics"][0]["measure"] == "lowestValidBidValue"
    assert result["bids"]["statistics"][0]["value"] == 1230000
    assert result["bids"]["statistics"][0]["currency"] == "EUR"
    assert result["bids"]["statistics"][0]["relatedLot"] == "LOT-0001"

def test_merge_tender_value_lowest():
    release_json = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "measure": "someOtherMeasure",
                    "value": 100000
                }
            ]
        }
    }
    
    tender_value_lowest_data = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "measure": "lowestValidBidValue",
                    "value": 1230000,
                    "currency": "EUR",
                    "relatedLot": "LOT-0001"
                }
            ]
        }
    }
    
    merge_tender_value_lowest(release_json, tender_value_lowest_data)
    
    assert len(release_json["bids"]["statistics"]) == 1
    assert release_json["bids"]["statistics"][0]["id"] == "1"
    assert release_json["bids"]["statistics"][0]["measure"] == "lowestValidBidValue"
    assert release_json["bids"]["statistics"][0]["value"] == 1230000
    assert release_json["bids"]["statistics"][0]["currency"] == "EUR"
    assert release_json["bids"]["statistics"][0]["relatedLot"] == "LOT-0001"

def test_bt_710_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:LowerTenderAmount currencyID="EUR">1230000</cbc:LowerTenderAmount>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_tender_value_lowest.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 1
    assert result["bids"]["statistics"][0]["id"] == "1"
    assert result["bids"]["statistics"][0]["measure"] == "lowestValidBidValue"
    assert result["bids"]["statistics"][0]["value"] == 1230000
    assert result["bids"]["statistics"][0]["currency"] == "EUR"
    assert result["bids"]["statistics"][0]["relatedLot"] == "LOT-0001"

if __name__ == "__main__":
    pytest.main()