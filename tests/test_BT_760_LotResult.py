# tests/test_BT_760_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_760_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                <efac:ReceivedSubmissionsStatistics>
                    <efbc:StatisticsCode listName="received-submission-type">t-sme</efbc:StatisticsCode>
                </efac:ReceivedSubmissionsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_received_submissions_type.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None, "Result is None"
    print(f"Full result: {json.dumps(result, indent=2)}")

    assert "bids" in result, "No 'bids' in result"
    assert "statistics" in result["bids"], "No 'statistics' in result['bids']"
    assert len(result["bids"]["statistics"]) == 1, f"Expected 1 statistic, got {len(result['bids']['statistics'])}"
    
    statistic = result["bids"]["statistics"][0]
    print(f"Statistic details: {json.dumps(statistic, indent=2)}")
    
    assert statistic["id"] == "1", f"Expected statistic id '1', got '{statistic.get('id')}'"
    assert statistic["measure"] == "smeBids", f"Expected measure 'smeBids', got '{statistic.get('measure')}'"
    assert statistic["relatedLot"] == "LOT-0001", f"Expected relatedLot 'LOT-0001', got '{statistic.get('relatedLot')}'"

if __name__ == "__main__":
    pytest.main()