import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_bt_196_bt_636_lot_result_integration(tmp_path):
    xml_content = """
    <root xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
          xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <efac:NoticeResult>
            <efac:LotResult>
                <efac:AppealRequestsStatistics>
                    <efbc:StatisticsCode listName="irregularity-type">code</efbc:StatisticsCode>
                    <efac:FieldsPrivacy>
                        <efbc:FieldIdentifierCode>buy-rev-typ</efbc:FieldIdentifierCode>
                        <efbc:ReasonDescription>Information delayed publication because of sensitive data</efbc:ReasonDescription>
                    </efac:FieldsPrivacy>
                </efac:AppealRequestsStatistics>
            </efac:LotResult>
        </efac:NoticeResult>
    </root>
    """
    xml_file = tmp_path / "test_input_bt_196_bt_636_lot_result.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "withheldInformation" in result, "Expected 'withheldInformation' in result"
    assert len(result["withheldInformation"]) == 1, f"Expected 1 withheld information item, got {len(result['withheldInformation'])}"

    withheld_info = result["withheldInformation"][0]
    assert "rationale" in withheld_info, "Expected 'rationale' in withheld information"
    expected_rationale = "Information delayed publication because of sensitive data"
    assert withheld_info["rationale"] == expected_rationale, f"Expected rationale '{expected_rationale}', got {withheld_info['rationale']}"

if __name__ == "__main__":
    pytest.main()