# tests/test_BT_538_Part.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_538_part_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:ProcurementProject>
                <cac:PlannedPeriod>
                    <cbc:DescriptionCode listName="timeperiod">UNLIMITED</cbc:DescriptionCode>
                </cac:PlannedPeriod>
            </cac:ProcurementProject>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_duration_other.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "contractPeriod" in result["tender"], "Expected 'contractPeriod' in tender"
    assert (
        "description" in result["tender"]["contractPeriod"]
    ), "Expected 'description' in tender contractPeriod"
    expected_description = "UNLIMITED"
    assert (
        result["tender"]["contractPeriod"]["description"] == expected_description
    ), f"Expected description '{expected_description}', got {result['tender']['contractPeriod']['description']}"


if __name__ == "__main__":
    pytest.main()
