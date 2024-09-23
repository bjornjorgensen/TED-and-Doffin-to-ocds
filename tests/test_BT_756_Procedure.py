# tests/test_BT_756_Procedure.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_bt_756_procedure_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:TerminatedIndicator>true</cbc:TerminatedIndicator>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_pin_competition_termination.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "tender" in result, "Expected 'tender' in result"
    assert "status" in result["tender"], "Expected 'status' in tender"
    assert (
        result["tender"]["status"] == "complete"
    ), f"Expected tender status 'complete', got {result['tender']['status']}"


def test_bt_756_procedure_integration_false(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:TenderingProcess>
            <cbc:TerminatedIndicator>false</cbc:TerminatedIndicator>
        </cac:TenderingProcess>
    </root>
    """
    xml_file = tmp_path / "test_input_pin_competition_termination_false.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "status" not in result.get(
        "tender",
        {},
    ), "Did not expect 'status' in tender when TerminatedIndicator is false"


if __name__ == "__main__":
    pytest.main()
