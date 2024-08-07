# tests/test_BT_712b_LotResult.py

import pytest
from lxml import etree
from converters.BT_712b_LotResult import parse_buyer_review_complainants_bt_712b, merge_buyer_review_complainants_bt_712b

def test_parse_buyer_review_complainants_bt_712b():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
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
    
    result = parse_buyer_review_complainants_bt_712b(xml_content)
    
    assert result is not None
    assert "statistics" in result
    assert len(result["statistics"]) == 1
    assert result["statistics"][0]["id"] == "1"
    assert result["statistics"][0]["value"] == 2
    assert result["statistics"][0]["measure"] == "complainants"
    assert result["statistics"][0]["scope"] == "complaints"
    assert result["statistics"][0]["relatedLot"] == "LOT-0001"

def test_merge_buyer_review_complainants_bt_712b():
    release_json = {
        "statistics": [
            {
                "id": "1",
                "value": 1,
                "measure": "appeals",
                "scope": "complaints",
                "relatedLot": "LOT-0001"
            }
        ]
    }
    
    buyer_review_complainants_data = {
        "statistics": [
            {
                "id": "2",
                "value": 2,
                "measure": "complainants",
                "scope": "complaints",
                "relatedLot": "LOT-0001"
            }
        ]
    }
    
    merge_buyer_review_complainants_bt_712b(release_json, buyer_review_complainants_data)
    
    assert len(release_json["statistics"]) == 2
    assert release_json["statistics"][1]["id"] == "2"
    assert release_json["statistics"][1]["value"] == 2
    assert release_json["statistics"][1]["measure"] == "complainants"
    assert release_json["statistics"][1]["scope"] == "complaints"
    assert release_json["statistics"][1]["relatedLot"] == "LOT-0001"

if __name__ == "__main__":
    pytest.main()