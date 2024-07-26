# tests/test_BT_636_LotResult.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_636_lot_result_integration(tmp_path):
    xml_content = """
    <root xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="irregularity-type">unj-lim-subc</efbc:StatisticsCode>
                </efac:AppealRequestsStatistics>
                <efac:TenderLot>
                    <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                </efac:TenderLot>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_irregularity_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "statistics" in result, "Expected 'statistics' in result"
    assert len(result["statistics"]) == 1, f"Expected 1 statistic, got {len(result['statistics'])}"

    statistic = result["statistics"][0]
    assert statistic["id"] == "1", f"Expected statistic id '1', got {statistic['id']}"
    assert statistic["measure"] == "unj-lim-subc", f"Expected measure 'unj-lim-subc', got {statistic['measure']}"
    assert statistic["scope"] == "complaints", f"Expected scope 'complaints', got {statistic['scope']}"
    assert statistic["notes"] == "Unjustified limitation of subcontracting", f"Expected notes 'Unjustified limitation of subcontracting', got {statistic['notes']}"
    assert statistic["relatedLot"] == "LOT-0001", f"Expected relatedLot 'LOT-0001', got {statistic['relatedLot']}"

if __name__ == "__main__":
    pytest.main()