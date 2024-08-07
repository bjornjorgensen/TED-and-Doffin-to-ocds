# tests/test_BT_760_LotResult.py

import pytest
from lxml import etree
from converters.BT_760_LotResult import parse_received_submissions_type, merge_received_submissions_type, SUBMISSION_TYPE_MAPPING

def test_parse_received_submissions_type():
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:ReceivedSubmissionsStatistics>
                    <efbc:StatisticsCode listName="received-submission-type">t-sme</efbc:StatisticsCode>
                </efac:ReceivedSubmissionsStatistics>
                <efac:ReceivedSubmissionsStatistics>
                    <efbc:StatisticsCode listName="received-submission-type">t-esubm</efbc:StatisticsCode>
                </efac:ReceivedSubmissionsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    
    result = parse_received_submissions_type(xml_content)
    
    assert result is not None
    assert "bids" in result
    assert "statistics" in result["bids"]
    assert len(result["bids"]["statistics"]) == 2
    assert result["bids"]["statistics"][0]["measure"] == "smeBids"
    assert result["bids"]["statistics"][1]["measure"] == "electronicBids"
    assert result["bids"]["statistics"][0]["relatedLot"] == "LOT-0001"
    assert result["bids"]["statistics"][1]["relatedLot"] == "LOT-0001"

def test_merge_received_submissions_type():
    release_json = {
        "bids": {
            "statistics": [
                {
                    "id": "1",
                    "measure": "totalBids",
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
                    "measure": "smeBids",
                    "relatedLot": "LOT-0001"
                },
                {
                    "id": "3",
                    "measure": "electronicBids",
                    "relatedLot": "LOT-0001"
                }
            ]
        }
    }
    
    merge_received_submissions_type(release_json, received_submissions_data)
    
    assert len(release_json["bids"]["statistics"]) == 3
    assert release_json["bids"]["statistics"][1]["measure"] == "smeBids"
    assert release_json["bids"]["statistics"][2]["measure"] == "electronicBids"

def test_all_submission_types_mapped():
    for xml_code, ocds_measure in SUBMISSION_TYPE_MAPPING.items():
        xml_content = f"""
        <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
              xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
              xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
            <efac:NoticeResult>
                <efac:LotResult>
                    <cbc:ID schemeName="result">RES-0001</cbc:ID>
                    <efac:ReceivedSubmissionsStatistics>
                        <efbc:StatisticsCode listName="received-submission-type">{xml_code}</efbc:StatisticsCode>
                    </efac:ReceivedSubmissionsStatistics>
                    <efac:TenderLot>
                        <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                    </efac:TenderLot>
                </efac:LotResult>
            </efac:NoticeResult>
        </root>
        """
        result = parse_received_submissions_type(xml_content)
        assert result["bids"]["statistics"][0]["measure"] == ocds_measure

if __name__ == "__main__":
    pytest.main()