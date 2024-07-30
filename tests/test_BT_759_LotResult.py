# tests/test_BT_759_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_759_lotresult_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:NoticeResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0001</cbc:ID>
                                <efac:ReceivedSubmissionsStatistics>
                                    <efbc:StatisticsNumeric>12</efbc:StatisticsNumeric>
                                </efac:ReceivedSubmissionsStatistics>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                            <efac:LotResult>
                                <cbc:ID schemeName="result">RES-0002</cbc:ID>
                                <efac:ReceivedSubmissionsStatistics>
                                    <efbc:StatisticsNumeric>8</efbc:StatisticsNumeric>
                                </efac:ReceivedSubmissionsStatistics>
                                <efac:TenderLot>
                                    <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
                                </efac:TenderLot>
                            </efac:LotResult>
                        </efac:NoticeResult>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </root>
    """
    xml_file = tmp_path / "test_input_received_submissions_count.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "bids" in result, "Expected 'bids' in result"
    assert "statistics" in result["bids"], "Expected 'statistics' in bids"
    assert len(result["bids"]["statistics"]) == 2, f"Expected 2 statistics, got {len(result['bids']['statistics'])}"

    stat1 = next(stat for stat in result["bids"]["statistics"] if stat["relatedLot"] == "LOT-0001")
    stat2 = next(stat for stat in result["bids"]["statistics"] if stat["relatedLot"] == "LOT-0002")

    assert stat1["value"] == 12, f"Expected value 12 for LOT-0001, got {stat1['value']}"
    assert stat2["value"] == 8, f"Expected value 8 for LOT-0002, got {stat2['value']}"

if __name__ == "__main__":
    pytest.main()